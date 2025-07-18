from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os

load_dotenv() #carrega as variáveis 
# Inicializa o cliente da Amadeus com as credenciais da API (armazenadas no .env)
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)
# Função que consulta a API da Amadeus com os dados fornecidos
def buscar_voos(origem_iata: str, destino_iata: str, data: str) -> list | dict:
    #print(f"DEBUG: Chamando API Amadeus: origem={origem_iata}, destino={destino_iata}, data={data}")

    try:
        #chamada principal à API amadeus com parametros de busca
        resposta = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origem_iata,
            destinationLocationCode=destino_iata,
            departureDate=data,
            adults=1,
            max=5 # Número máximo de resultados retornados
        )
        if resposta.data:
            print("DEBUG: Resposta da Amadeus recebida (api/amadeus_client.py).")
            return resposta.data # Retorna os dados brutos da Amadeus (lista de voos)
        else:
            #print("DEBUG: Amadeus não encontrou voos para a pesquisa.")
            # Retorna um dicionário indicando que não houve dados (não é um erro técnico da API)
            return {"api_status": "NO_DATA", "message": "Nenhum voo encontrado pela Amadeus para os critérios fornecidos."}
            
    except ResponseError as error:
        print(f"ERRO da Amadeus (api/amadeus_client.py): {error}")
        # Retorna um dicionário de erro específico para a camada superior interpretar
        error_detail = "Erro desconhecido da Amadeus."
        # Tenta extrair mensagem de erro detalhada da resposta da Amadeus
        if error.response and error.response.result:
            amadeus_errors = error.response.result.get('errors', [])
            if amadeus_errors:
                error_detail = amadeus_errors[0].get('detail', amadeus_errors[0].get('title', str(error)))
            else:
                error_detail = str(error)
        # Retorna o erro formatado como dicionário
        return {
            "api_error": True, 
            "status_code": error.code, 
            "message": error_detail
        }
        
    except Exception as e:
        print(f"ERRO INESPERADO (api/amadeus_client.py): {str(e)}")
        # Erro genérico
        return {
            "api_error": True, 
            "status_code": 500, 
            "message": f"Erro interno na conexão com Amadeus: {str(e)}"}
