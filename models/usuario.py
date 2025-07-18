from langchain_core.messages import HumanMessage, AIMessage 

class Usuario:
    def __init__(self, nome, finalidade, dadosviagem=None, preferencias=None, chat_history=None):
        self.nome = nome
        self.finalidade = finalidade
        # Se dadosviagem não for fornecido, inicializa com valores padrão None
        self.dadosviagem = dadosviagem or {
            "origem": None,
            "destino": None,
            "dia": None
        }
         # Preferências padrão, se não fornecidas, com chave clima nula
        self.preferencias = preferencias or {
            "clima": None
        }
        # Histórico de mensagens do chat, vazio se não fornecido
        self.chat_history = chat_history or []

    def atualizar_preferencia(self, chave, valor): #Atualiza o valor de uma preferência existente.
        if chave in self.preferencias:
            self.preferencias[chave] = valor

    def to_dict(self): #Serializa o objeto Usuario em um dicionário para salvar ou manipular
        return {
            "nome": self.nome,
            "finalidade": self.finalidade,
            "dados": self.dadosviagem,
            "preferencias": self.preferencias,
            "chat_history": self.chat_history
        }

    @staticmethod
    def from_dict(d): #Cria uma instância Usuario a partir de um dicionário.
        #Reconstrói o histórico de chat transformando dicionários em objetos HumanMessage e AIMessage.
        chat_history = []
        for msg in d.get("chat_history", []):
            tipo = msg.get("type")
            content = msg.get("content", "").strip()
            if not content:
                continue  # Ignora mensagens vazias
            if tipo == "human" :
                chat_history.append(HumanMessage(content=content))
            elif tipo == "ai":
                chat_history.append(AIMessage(content=content))    
        return Usuario( # Usa a lista reconstruída
            nome=d["nome"],
            finalidade=d.get("finalidade"),
            dadosviagem=d.get("dados"),
            preferencias=d.get("preferencias"),
            chat_history=d.get("chat_history")
        )