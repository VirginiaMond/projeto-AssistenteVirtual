from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from config.settings import llm
from memory import obter_ou_criar_usuario, carregar_memoria, salvar_memoria
from langchain_core.messages import BaseMessage


memoria = carregar_memoria()

def get_history_for_langchain(session_id: str) -> InMemoryChatMessageHistory:
    history = InMemoryChatMessageHistory()
    user_obj = memoria.get(session_id)
    if user_obj and hasattr(user_obj, 'chat_history'):
        for item in user_obj.chat_history:
            if isinstance(item, BaseMessage):
                history.messages.append(item)
            elif isinstance(item, dict):
                if "pergunta" in item:
                    history.add_user_message(item["pergunta"])
                if "resposta" in item:
                    history.add_ai_message(item["resposta"])
   
    return history

llm_com_memoria = RunnableWithMessageHistory(
    RunnableLambda(lambda d: llm.invoke(d.get("history", []) + d["messages"])),
    get_history_for_langchain,
    input_messages_key="messages",
    history_messages_key="history"
)
