from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from config.settings import llm
from memory import criar_usuario, carregar_memoria, salvar_memoria
from langchain_core.messages import BaseMessage


memoria = carregar_memoria() #carrega a memoria existente

def get_history_for_langchain(session_id: str) -> InMemoryChatMessageHistory:
    #inicializa um historico em memoria vazio
    history = InMemoryChatMessageHistory()
    user_obj = memoria.get(session_id) #recupera o objeto do usuario pela sessao
    #se existir histórico salvo, adc o objeto do langchain
    if user_obj and hasattr(user_obj, 'chat_history'):
        for item in user_obj.chat_history:
            if isinstance(item, BaseMessage):
                history.messages.append(item) #msg no formato correto
            elif isinstance(item, dict):
                # Suporte a registros no formato antigo (dicionário com 'pergunta' e 'resposta')
                if "pergunta" in item:
                    history.add_user_message(item["pergunta"])
                if "resposta" in item:
                    history.add_ai_message(item["resposta"])
   
    return history # Retorna o histórico pronto para ser usado no LLM

def filtrar_mensagens_validas(mensagens: list[BaseMessage]) -> list[BaseMessage]:
    #retorna apenas mensagens com conteudo nao vazio
    return [msg for msg in mensagens if getattr(msg, "content", None) and msg.content.strip()]

#criação do LLM com historico manual
llm_com_memoria = RunnableWithMessageHistory(
    RunnableLambda(lambda d: llm.invoke(
        #executa o modelo com 3 partes: msg tipo system, historico de msg validas e msg novas exceto system
        [m for m in d.get("messages", []) if m.type == "system"] +
        [m for m in d.get("history", []) if getattr(m, "content", None) and m.content.strip() != ""] +
        [m for m in d.get("messages", []) if m.type != "system" and getattr(m, "content", None) and m.content.strip() != ""]
        )
    ),
    get_history_for_langchain, #recupera e converte o historico salvo para formato aceito pelo langchain
    input_messages_key="messages", # Chave onde ficam as mensagens atuais
    history_messages_key="history" # Chave que representa o histórico anterior
)
