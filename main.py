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

def iniciar_chat_terminal():
    #carrega os dados de usuário salvo 
    memoria = carregar_memoria()
    if memoria is None:
        memoria = {}
    
    print("=== Assistente Virtual Mochi ^^ ===")
    username = input("Por gentileza, me diga seu nome/id que queira utilizar: ")
    usuario = criar_usuario(username, memoria)
    #se n estiver preenchido, define
    if not hasattr(usuario, 'nome') or usuario.nome is None:
        usuario.nome = username

    agente_passagens = criar_agente(llm, usuario) #cria o agente que será usado para buscar passagens
    awaiting_search_confirmation = False #flag para saber se o usuário está prestes a confirmar a busca

    while True:
        entrada = input("\nVocê: ")
        if entrada.lower() in ["sair", "exit"]:
            print("Mochi: Espero que eu tenha ajudado! Obrigado por me escolher... bye bye!")
            salvar_memoria(memoria)
            break
        #atualiza os dados extraidos da frase
        atualizar_dados_usuario(entrada, usuario)
        salvar_memoria(memoria)
        
        #logica para confirmar busca
        if awaiting_search_confirmation:
            if "sim" in entrada.lower():
                print("BOT: Ótimo! Realizando a busca de passagens agora...")
                if executar_agente("buscar passagens", usuario, agente_passagens):
                    salvar_memoria(memoria)
                else:
                    print("BOT: Não foi possível realizar a busca mesmo com a confirmação.")
                awaiting_search_confirmation = False
                continue
            elif "não" in entrada.lower():
                print("BOT: Entendido. Posso te ajudar com outra coisa?")
                awaiting_search_confirmation = False
                salvar_memoria(memoria)
                continue
        #monta o contexto da conversa
        contexto = construir_contexto(usuario, entrada)
        human_message_content = contexto.strip()
        
        if not human_message_content: #se estiver vazio
            human_message_content = "Informações de contexto e entrada do usuário foram fornecidas, mas sem conteúdo específico."
        #carrega instruções/prompt inicial do sistema 
        system_message_content = instrucoes_mochi.strip()
        if not system_message_content:
            system_message_content = "Você é um assistente de viagens de IA."

        #print("DEBUG - CONTEXTO:", contexto)
        #cria a sequencia de mensagens para o LLM
        mensagens = [
            SystemMessage(content=system_message_content)
        ]
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
            print("BOT:", texto_resposta)
        
        #tratamentos de erros
        except (ResourceExhausted, InvalidArgument) as e:
            print(f"BOT: Ocorreu um erro ao comunicar com a IA (Quota Excedida ou Argumento Inválido). Erro: {e}")
            texto_resposta = "Erro de serviço da IA. Por favor, tente novamente mais tarde."
            print("BOT:", texto_resposta)
        except Exception as e:
            print(f"BOT: Ocorreu um erro inesperado: {e}")
            texto_resposta = "Erro interno do chatbot. Tente novamente."
            print("BOT:", texto_resposta)
        
        #atualiza o historico
        if usuario.chat_history is None:
            usuario.chat_history = []
        #adiciona pergunta e resposta ao historico
        entrada = entrada.strip() if entrada.strip() else "(Pergunta do usuário vazia)"
        texto_resposta = texto_resposta.strip() if texto_resposta.strip() else "(Resposta do BOT vazia)"
        usuario.chat_history.append(HumanMessage(content=entrada))
        usuario.chat_history.append(AIMessage(content=texto_resposta))
        
        #recupera dados mais recentes do usuario
        prefs = usuario.preferencias
        dadosnovos = usuario.dadosviagem
        finalidade = usuario.finalidade
        origem = dadosnovos.get("origem")
        destino = dadosnovos.get("destino")
        dia = dadosnovos.get("dia")
        
        dados_completos = origem and destino and dia

        #confirma ou aciona busca automática
        if dados_completos and not awaiting_search_confirmation:
            if finalidade == "trabalho": 
                print("BOT: Tenho todos os dados para sua viagem a trabalho. Deseja que eu realize a busca agora? (sim/não)")
                awaiting_search_confirmation = True
                salvar_memoria(memoria)
                continue
            elif finalidade == "lazer":
                print("BOT: Que legal! Sua viagem a lazer está toda definida. Quando quiser, posso ajudar a buscar as passagens. Deseja agora? (sim/não)")
                awaiting_search_confirmation = True
                salvar_memoria(memoria)
                continue
        # Caso o usuário mencione algo que sugira busca de passagem, faz diretamente
        elif deve_buscar_passagem(entrada) and not awaiting_search_confirmation:
            sucesso = executar_agente(entrada, usuario, agente_passagens)
            if sucesso:
                salvar_memoria(memoria)
        
        salvar_memoria(memoria)


if __name__ == "__main__":
    iniciar_chat_terminal()
