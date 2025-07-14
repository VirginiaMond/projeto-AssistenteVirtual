
class Usuario:
    def __init__(self, nome, preferencias=None, chat_history=None,dados=None):
        self.nome = nome
        self.preferencias = preferencias or {
            "clima": None,
            "lugares": [],
            "restricoes": [],
            "preferencias": [],
            "finalidade": None 
        }
        self.chat_history = chat_history or []
        self.dados = dados or {
            "origem": None,
            "destino": None,
            "dia": None
        }

    def atualizar_preferencia(self, chave, valor):
        if chave in self.preferencias:
            self.preferencias[chave] = valor

    def to_dict(self):
        return {
            "nome": self.nome,
            "preferencias": self.preferencias,
            "chat_history": self.chat_history,
            "dados": self.dados
        }

    @staticmethod
    def from_dict(d):
        return Usuario(
            nome=d["nome"],
            preferencias=d.get("preferencias"),
            chat_history=d.get("chat_history"),
            dados=d.get("dados")
        )