from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool, StructuredTool
from tools.viagens_api import buscar_passagens
from config.settings import llm
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field #validar oque a ferramenta(tool) espera receber

class BuscaPassagensInput(BaseModel):
    origem: str = Field(description="A cidade ou aeroporto de partida do voo. Ex: 'São Luís', 'GRU'.")
    destino: str = Field(description="A cidade ou aeroporto de chegada do voo. Ex: 'São Paulo', 'SDU'.")
    data: str = Field(description="A data da viagem (ida).")

#criação do agente especializado em passagens
def criar_agente(llm, usuario):
    ferramentas = [ #criação da ferramenta BuscaPassagens
        StructuredTool.from_function(
            func=buscar_passagens, #chama a função que contém o chamado à API
            name="BuscaPassagens",
            description=""" 
            Útil para buscar passagens aéreas e responder a perguntas sobre voos e preços.
            Esta ferramenta DEVE ser usada apenas quando o usuário solicitar informações 
                específicas sobre passagens.
            A ferramenta requer e DEVE receber EXATAMENTE os seguintes parâmetros:
            - 'origem' (str): A cidade ou aeroporto de partida do voo. Ex: "São Luís", "GRU".
            - 'destino' (str): A cidade ou aeroporto de chegada do voo. Ex: "São Paulo", "SDU".
            - 'data' (str): A data da viagem (ida). 
            **Instruções para extrair os parâmetros:**
            Você receberá um 'input' que pode conter as informações formatadas como 
                'Origem: [valor]', 'Destino: [valor]', 'Data: [valor]' ou na forma de texto livre.
            1.  Primeiro, procure por "Origem: " ou nome de lugares com aeroporto na entrada para
                identificar o 'origem'.
            2.  Em seguida, procure por "Destino: " ou nome de lugares com aeroporto para
                identificar o 'destino'.
            3.  Finalmente, procure por "Data: " ou "dia " para identificar a 'data'.
            4.  **Se alguma dessas informações (origem, destino, data) estiver faltando 
                ou for ambígua/inválida:**
                NÃO chame a ferramenta. Em vez disso, retorne a string "ERRO_BUSCA_PASSAGENS".
            Exemplo: Se faltar origem e data, retorne "ERRO_BUSCA_PASSAGENS: origem,data".          
           """,
            args_schema=BuscaPassagensInput, #garante obrigatoriedade
            return_direct=True
        )
    ]

    agent = initialize_agent( #inicializa o agente com ferramenta
        tools=ferramentas,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS, # Usa o modelo no estilo "function calling"
        verbose=False, # Exibe logs no terminal
        agent_kwargs={
            "system_message": SystemMessage(content="""
            Você é um agente de software especializado em extrair informações de viagem e
            chamar a ferramenta 'BuscaPassagens'.
            Sua única tarefa é analisar o 'input' fornecido, extrair a Origem, Destino e 
            Data da viagem e retornar a resposta.

            **Procedimento Rigoroso:**
            1.  Analise o 'input' fornecido. O input pode conter informações já extraídas e
                formatadas ou texto livre do usuário.
            2.  Identifique a Origem, Destino e Data.
            3.  **Se todas as três informações (origem, destino, data) forem claramente
                identificáveis e válidas:**
                Chame a ferramenta 'BuscaPassagens' com esses parâmetros.
            4.  **Se alguma dessas informações (origem, destino, data) estiver faltando ou 
                for ambígua/inválida:**
                NÃO chame a ferramenta. Em vez disso, retorne a string
                 "INFORMACOES_INSUFICIENTES".
            5.  NÃO adicione nenhum texto conversacional ou explicação além do retorno da
                ferramenta ou da string "INFORMACOES_INSUFICIENTES".
            """
            )
        }
    )

    return agent
