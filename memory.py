import json
import os
from models.usuario import Usuario
from config.settings import DATA_PATH
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
#Função de carregar a memória 
def carregar_memoria():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f: #abre o arquivo
            conteudo = f.read().strip()
            if not conteudo: #se o arquivo estiver vazio
                return {}
            bruto = json.loads(conteudo) #carrega os dados json como dicionario
            memoria = {}
            #Para cada usuario salvo
            for nome, dados in bruto.items():
                #garante que nao seja uma tupla
                finalidade = dados.get("finalidade")
                if isinstance(finalidade, tuple):
                    finalidade = finalidade[0] if finalidade else None
                chat_history = []
                #reconstroi o historico de mensagens
                for msg in dados.get("chat_history", []):
                    content = msg.get("content", "").strip()
                    if not content:
                        continue #ignora mensagens vazias
                    
                    #cria objeto HumanMessage ou AIMEssage conforme o tipo
                    if msg.get("type") == "human":
                        chat_history.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("type") == "ai":
                        chat_history.append(AIMessage(content=msg.get("content", "")))
                
                #cria e adiciona o objeto Usuario à memória
                memoria[nome] = Usuario(
                    nome=dados.get("nome"),
                    finalidade=dados.get("finalidade"),
                    dadosviagem = dados.get("dados"),
                    preferencias=dados.get("preferencias", {}),
                    chat_history=chat_history
                )
            return memoria #retorna o dicionário com todos os usuários
    except FileNotFoundError: #para arquivo inexistente
        return {}
    except json.JSONDecodeError: #para arquivo corrompido
        return {}

def serializar_mensagem(mensagem: BaseMessage):
    #converte uma msg para dicionario serializável em JSON
    return {
        "type": mensagem.type,
        "content": mensagem.content
    }

def salvar_memoria(memoria):
    #Garante que o diretório do arquivo de memória exista
    pasta = os.path.dirname(DATA_PATH)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    #constroi o dicionario com todos os dados dos usuários
    data = {
        nome: {
            "nome": usuario.nome,
            "finalidade": usuario.finalidade,
            "dados": usuario.dadosviagem,
            "preferencias": usuario.preferencias,
            "chat_history": [
                serializar_mensagem(m) 
                for m in usuario.chat_history if m.content.strip() != ""
            ]
        }
        for nome, usuario in memoria.items()
    }
    #salva o conteúdo no arquivo JSON com indentação
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def criar_usuario(username, memoria):
    #cria um novo usuário na memória se ele ainda n existir
    if username not in memoria:
        memoria[username] = Usuario(
            nome=username,
            finalidade= None,
            dadosviagem = None,
            preferencias={
                "clima": None
            }, 
            chat_history=[]
            
        )
    return memoria[username]
