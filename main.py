from memory import carregar_memoria, salvar_memoria, obter_ou_criar_usuario
from config.settings import llm
from agent import criar_agente
from history import get_history_for_langchain, llm_com_memoria
from context import construir_contexto
from agent_run import executar_agente
from regex import atualizar_dados_usuario
from prompt import instrucoes_botfly
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from google.api_core.exceptions import ResourceExhausted, InvalidArgument
from utils.formatters import deve_buscar_passagem

def iniciar_chat_terminal():
    memoria = carregar_memoria()
    if memoria is None:
        memoria = {}
    print("=== Chatbot Viagens ===")
    username = input("Seja bem vindo ao SkIA! Por gentileza, me diga seu nome/id: ")
    usuario = obter_ou_criar_usuario(username, memoria)
    if not hasattr(usuario, 'nome') or usuario.nome is None:
        usuario.nome = username

    agente_passagens = criar_agente(llm, usuario)
    awaiting_search_confirmation = False

    while True:
        entrada = input("\nVocê: ")
        if entrada.lower() in ["sair", "exit"]:
            print("Botfly: Espero que eu tenha ajudado! Obrigado por me escolher... bye bye!")
            salvar_memoria(memoria)
            break

        atualizar_dados_usuario(entrada, usuario)

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

        contexto = construir_contexto(usuario, entrada)
        human_message_content = contexto.strip()
        
        if not human_message_content:
            human_message_content = "Informações de contexto e entrada do usuário foram fornecidas, mas sem conteúdo específico."

        system_message_content = instrucoes_botfly.strip()
        if not system_message_content:
            system_message_content = "Você é um assistente de IA."

        mensagens = [
            SystemMessage(content=system_message_content)
        ]
        if human_message_content:
            mensagens.append(HumanMessage(content=human_message_content))
        
        try:
            resposta = llm_com_memoria.invoke(
                {"messages": mensagens},
                config={"configurable": {"session_id": username}}
            )
            texto_resposta = resposta.content if isinstance(resposta, AIMessage) else str(resposta)
            if not texto_resposta.strip(): # Fallback se a resposta do LLM for vazia
                texto_resposta = "Desculpe, não consegui gerar uma resposta significativa. Tente novamente."
            print("BOT:", texto_resposta)
        except (ResourceExhausted, InvalidArgument) as e:
            print(f"BOT: Ocorreu um erro ao comunicar com a IA (Quota Excedida ou Argumento Inválido). Erro: {e}")
            texto_resposta = "Erro de serviço da IA. Por favor, tente novamente mais tarde."
            print("BOT:", texto_resposta)
        except Exception as e:
            print(f"BOT: Ocorreu um erro inesperado: {e}")
            texto_resposta = "Erro interno do chatbot. Tente novamente."
            print("BOT:", texto_resposta)
        # --- FIM: Chamada ao LLM Principal com tratamento de erros ---

        if usuario.chat_history is None:
            usuario.chat_history = []
        entrada = entrada.strip() if entrada.strip() else "(Pergunta do usuário vazia)"
        texto_resposta = texto_resposta.strip() if texto_resposta.strip() else "(Resposta do BOT vazia)"
        usuario.chat_history.append(HumanMessage(content=entrada))
        usuario.chat_history.append(AIMessage(content=texto_resposta))
        prefs = usuario.preferencias
        origem = prefs.get("origem")
        destino = prefs.get("destino")
        data = prefs.get("dia")
        finalidade = prefs.get("finalidade")

        dados_completos = origem and destino and data

        if dados_completos and finalidade == "trabalho" and not awaiting_search_confirmation:
            print("BOT: Tenho todos os dados para sua viagem a trabalho. Deseja que eu realize a busca agora? (sim/não)")
            awaiting_search_confirmation = True
            salvar_memoria(memoria)
            continue
        elif deve_buscar_passagem(entrada) and not awaiting_search_confirmation:
            executar_agente(entrada, usuario, agente_passagens)
    
        salvar_memoria(memoria)


if __name__ == "__main__":
    iniciar_chat_terminal()
