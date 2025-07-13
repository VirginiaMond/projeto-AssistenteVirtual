import json
import os
from models.usuario import Usuario
from config.settings import DATA_PATH
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

def carregar_memoria():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return {}
            bruto = json.loads(conteudo)
            memoria = {}
            for nome, dados in bruto.items():
                chat_history = []
                for msg in dados.get("chat_history", []):
                    if msg.get("type") == "human":
                        chat_history.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("type") == "ai":
                        chat_history.append(AIMessage(content=msg.get("content", "")))
                memoria[nome] = Usuario(
                    nome=dados.get("nome"),
                    preferencias=dados.get("preferencias", {}),
                    chat_history=chat_history
                )
            return memoria
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def serializar_mensagem(mensagem: BaseMessage):
    return {
        "type": mensagem.type,
        "content": mensagem.content
    }


def serializar_mensagem(mensagem: BaseMessage):
    return {
        "type": mensagem.type,
        "content": mensagem.content
    }

def salvar_memoria(memoria):
    pasta = os.path.dirname(DATA_PATH)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    data = {
        nome: {
            "nome": usuario.nome,
            "preferencias": usuario.preferencias,
            "chat_history": [
                serializar_mensagem(m) for m in usuario.chat_history
            ]
        }
        for nome, usuario in memoria.items()
    }

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def obter_ou_criar_usuario(username, memoria):
    if username not in memoria:
        memoria[username] = Usuario(
            nome=username,
            preferencias={
                "clima": None,
                "lugares": [],
                "tipo": None,
                "restricoes": [],
                "finalidade": None
            }, 
            chat_history=[]
        )
    return memoria[username]
