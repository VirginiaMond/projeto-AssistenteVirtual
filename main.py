from memory import carregar_memoria, salvar_memoria, criar_usuario
from config.settings import llm
from agent import criar_agente
from history import get_history_for_langchain, llm_com_memoria
from context import construir_contexto
from agent_run import executar_agente
from regex import atualizar_dados_usuario
from prompt import instrucoes_mochi
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from google.api_core.exceptions import ResourceExhausted, InvalidArgument
from utils.formatters import deve_buscar_passagem
from datetime import datetime

def iniciar_chat_terminal():
    #carrega os dados de usuário salvo 
    memoria = carregar_memoria()
    if memoria is None:
        memoria = {}
    
    print("========== Assistente Virtual Mochi ^^ ==========")
    username = input("Por gentileza, me diga seu nome/id que queira utilizar: ")
    usuario = criar_usuario(username, memoria)
    #se n estiver preenchido, define
    if not hasattr(usuario, 'nome') or usuario.nome is None:
        usuario.nome = username

    agente_passagens = criar_agente(llm, usuario) #cria o agente que será usado para buscar passagens
    awaiting_search_confirmation = False #flag para saber se o usuário está prestes a confirmar a busca

    while True:
        entrada = input("\nVocê: ")
        salvar_memoria(memoria)
        if entrada.lower() in ["sair", "exit"]:
            print("Mochi: Tudo bem! Se precisar de mim depois, é só voltar — estarei por aqui. Boa viagem e até logo! ✈️🌟")
            salvar_memoria(memoria)
            break
        #atualiza os dados extraidos da frase
        atualizar_dados_usuario(entrada, usuario)
        salvar_memoria(memoria)
        
        #logica para confirmar busca
        if awaiting_search_confirmation:
            if "sim" in entrada.lower():
                print("MOCHI: Ótimo! Realizando a busca de passagens agora...")
                dados_passagens = executar_agente("buscar passagens", usuario, agente_passagens)
                if dados_passagens:
                    #Gera uma chave única baseada no timestamp
                    chave_passagem = f"busca_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
                    # Adiciona ao dicionário de passagens
                    if not hasattr(usuario, 'passagens') or not isinstance(usuario.passagens, dict):
                        usuario.passagens = {}
    
                    usuario.passagens[chave_passagem] = dados_passagens
                    #if not hasattr(usuario, 'passagens'):  
                        #usuario.passagens = {}  
                        # Adicione os dados
                    #usuario.passagens.append(dados_passagens)  
                    print("MOCHI: Aqui estão os dados das passagens encontradas:")
                    print(dados_passagens)
                    salvar_memoria(memoria)
                else:
                    print("MOCHI: Não foi possível realizar a busca no momento, pode tentar novamente mais tarde.")
                awaiting_search_confirmation = False
                continue
            elif "não" in entrada.lower():
                print("MOCHI: Entendido. Posso te ajudar com outra coisa?")
                awaiting_search_confirmation = False
                salvar_memoria(memoria)
                continue
        #monta o contexto da conversa
        contexto = construir_contexto(usuario, entrada)
        human_message_content = contexto.strip()
        
        if not human_message_content: #se estiver vazio
            human_message_content = "Informações de contexto e entrada do usuário foram fornecidas, mas sem conteúdo específico."
        #carrega instruções/prompt inicial do sistema 
        #system_message_content = instrucoes_mochi.strip()
        # Substituir instruções com nome do usuário
        system_message_content = instrucoes_mochi.strip().replace("{nome}", usuario.nome or username)

        if not system_message_content:
            system_message_content = "Você é um assistente de viagens de IA."

        #print("DEBUG - CONTEXTO:", contexto)
        #cria a sequencia de mensagens para o LLM
        mensagens = [
            SystemMessage(content=system_message_content)
        ]
        # Adiciona histórico anterior (limitando a 10 últimas interações, por segurança)
        #for msg in usuario.chat_history[-5:]:
            #mensagens.append(msg)
        
        if human_message_content:
            mensagens.append(HumanMessage(content=human_message_content))
        
        # Filtro para remover mensagens vazias (protegendo o Gemini)
        mensagens = [msg for msg in mensagens if msg.content and msg.content.strip()]

        try:
            #envia as mensagens para o modelo com memoria de sessão
            resposta = llm_com_memoria.invoke( 
                {"messages": mensagens},
                config={"configurable": {"session_id": username}}
            )
            #trata o retorno
            texto_resposta = resposta.content if isinstance(resposta, AIMessage) else str(resposta)
            if not texto_resposta.strip(): # Fallback se a resposta do LLM for vazia
                texto_resposta = "Desculpe, não consegui gerar uma resposta significativa. Tente novamente."
            print("MOCHI:", texto_resposta)
        
        #tratamentos de erros
        except (ResourceExhausted, InvalidArgument) as e:
            print(f"MOCHI: Ocorreu um erro ao comunicar com a IA (Quota Excedida ou Argumento Inválido). Erro: {e}")
            texto_resposta = "Erro de serviço da IA. Por favor, tente novamente mais tarde."
            print("MOCHI:", texto_resposta)
        except Exception as e:
            print(f"MOCHI: Ocorreu um erro inesperado: {e}")
            texto_resposta = "Erro interno do chatbot. Tente novamente."
            print("MOCHI:", texto_resposta)
        
        #atualiza o historico
        if usuario.chat_history is None:
            usuario.chat_history = []
        #adiciona pergunta e resposta ao historico
        entrada = entrada.strip() if entrada.strip() else "(Pergunta do usuário vazia)"
        texto_resposta = texto_resposta.strip() if texto_resposta.strip() else "(Resposta do BOT vazia)"
        # Evita duplicação de mensagens
        if not usuario.chat_history or usuario.chat_history[-1].content != entrada:
            usuario.chat_history.append(HumanMessage(content=entrada))
        if not usuario.chat_history or usuario.chat_history[-1].content != texto_resposta:
            usuario.chat_history.append(AIMessage(content=texto_resposta))
        
        #recupera dados mais recentes do usuario
        prefs = usuario.preferencias
        dadosnovos = usuario.dadosviagem
        finalidade = usuario.finalidade
        origem = dadosnovos.get("origem")
        destino = dadosnovos.get("destino")
        dia = dadosnovos.get("dia")
        
        dados_completos = origem and destino and dia

        # Caso o usuário já tenha dito para buscar
        if dados_completos and deve_buscar_passagem(entrada) and not awaiting_search_confirmation:
            print("MOCHI: Perfeito! Buscando passagens agora...")
            dados_passagens = executar_agente(entrada, usuario, agente_passagens)
            if dados_passagens:
                salvar_memoria(memoria)
            else:
                print("MOCHI: Não consegui encontrar passagens agora.")
            continue
        # Caso os dados estejam completos, mas o usuário ainda não pediu a busca
        elif dados_completos and not awaiting_search_confirmation:
            print("MOCHI: Deseja que eu realize a busca agora? (sim/não)")
            awaiting_search_confirmation = True
            salvar_memoria(memoria)
            continue
        
        # Se o usuário estiver respondendo "sim" após a pergunta
        elif entrada.lower() in ["sim", "pode buscar", "sim, por favor"] and awaiting_search_confirmation:
            print("MOCHI: Certo! Buscando as passagens agora...")
            dados_passagens = executar_agente(entrada, usuario, agente_passagens)
            if dados_passagens:
                salvar_memoria(memoria)
            else:
                print("MOCHI: Não consegui encontrar passagens agora.")
            awaiting_search_confirmation = False
            salvar_memoria(memoria)
            continue

        #confirma ou aciona busca automática
        # (Opcional) Detecta quando o usuário quer informar a finalidade
        elif "trabalho" in entrada.lower() or "lazer" in entrada.lower():
            finalidade = "trabalho" if "trabalho" in entrada.lower() else "lazer"
            print(f"MOCHI: Entendi que sua viagem é a passeio de {finalidade}. 😉")
            salvar_memoria(memoria)
            continue   
        
        salvar_memoria(memoria)


if __name__ == "__main__":
    iniciar_chat_terminal()
