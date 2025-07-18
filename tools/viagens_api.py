from datetime import datetime
import locale
from api.amadeus_client import buscar_voos
from api.formatador import formatar_voo

# Dicionário que mapeia nomes de cidades para seus respectivos códigos IATA de aeroportos
IATA_CODIGOS = {
    "são paulo": "GRU",
    "sao paulo": "GRU",
    "são luis": "SLZ",
    "sao luis": "SLZ",
    "fortaleza": "FOR",
    "itália": "AHO",
    "italia": "AHO",
    "brasilia": "BSB",
    "campo grande":"CGR",
    "imperatriz":"IMP",
    "macapá":"MCP",
    "macapa":"MCP",
    "china":"NKG",
    "korea":"SEL",
    "rio de janeiro":"SDU"
}

  #Verifica se a string de data já contém um ano entre 2023 e 2030.
    #Se não contiver, adiciona o ano atual ao final da string, no formato '... de YYYY'.
def completar_ano_se_faltando(data_str: str) -> str:
    """Adiciona o ano atual à string de data se ela não contiver ano."""
    if any(str(ano) in data_str for ano in range(2023, 2031)):  # já tem ano
        return data_str
    ano_atual = datetime.now().year
    return f"{data_str} de {ano_atual}"


    #Tenta definir o locale do sistema para português brasileiro, para garantir
    #que o parsing de datas com meses em português funcione corretamente.
    #Tenta primeiro para Linux/macOS, depois para Windows. Se não conseguir,
    #exibe um aviso.

def definir_locale_portugues():
    try:
        # Para Linux/macOS
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        print("Locale definido: pt_BR.UTF-8")
    except locale.Error:
        try:
        # Para Windows
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            print("Locale definido: Portuguese_Brazil.1252")
        except locale.Error:
            print("⚠️ WARNING: Locale pt_BR não disponível. Parser de datas com mês em português pode falhar.")

    #Recebe uma string de data e coloca as palavras que não são preposições
    #com a primeira letra maiúscula, para melhorar o parsing da data.
    #Exemplo: '20 de março de 2025' -> '20 de Março de 2025'
def corrigir_data(data):
    partes = data.lower().split()
    for i, palavra in enumerate(partes):
        if palavra not in ['de', 'do', 'da', 'e']:
            partes[i] = palavra.capitalize()
    return ' '.join(partes)



    #Função principal que busca passagens aéreas usando a API Amadeus,
    #dado origem, destino e data da viagem.
def buscar_passagens(origem: str, destino: str, data: str):
    print(f"DEBUG: data recebida do agente: {data}")
    definir_locale_portugues() 
    
    try:
        origem_iata = IATA_CODIGOS.get(origem.lower()) 
        destino_iata = IATA_CODIGOS.get(destino.lower()) 
        if not origem_iata:
            return "ERRO_FERRAMENTA:Código IATA para '{origem}' não encontrado. Por favor, especifique uma cidade como 'São Paulo' ou 'Fortaleza'."
        if not destino_iata:
            return "ERRO_FERRAMENTA:Código IATA para '{destino}' não encontrado. Por favor, especifique uma cidade como 'São Paulo' ou 'Fortaleza'."

         # Corrige a formatação da data para facilitar o parsing
        data_corrigida = corrigir_data(data.strip())
        data_corrigida = completar_ano_se_faltando(data_corrigida)
        print(f"DEBUG: Data corrigida para parses: '{data_corrigida}'")

        # Formatos possíveis para tentar converter a string em objeto datetime
        formatos = ["%d de %B de %Y", "%d/%m/%Y", "%Y-%m-%d"]
        data_formatada = None

         # Tenta converter a data para objeto datetime usando os formatos listados
        for fmt in formatos:
            try:
                data_obj = datetime.strptime(data_corrigida, fmt)
                data_formatada = data_obj.strftime("%Y-%m-%d")  # Formato ISO
                print(f"DEBUG: Data formatada para API: '{data_formatada}'")
                break
            except ValueError:
                continue
            
        if not data_formatada:
            return "ERRO_FERRAMENTA: Data no formato inválido. Use 'DD/MM/AAAA' ou 'DD de mês de AAAA'."
        
        print(f"DEBUG: Enviando requisição Amadeus Flight Offers Search: origem_iata='{origem_iata}', destino_iata='{destino_iata}', data='{data_formatada}'")

        # 🔁 Usa a função da Amadeus
        voos = buscar_voos(origem_iata, destino_iata, data_formatada)
        # Verifica se houve erro na resposta da API
        if isinstance(voos, dict) and ("api_error" in voos or "api_status" in voos):
            return f"ERRO_FERRAMENTA: Erro ao consultar a API: {voos.get('api_error') or voos.get('api_status')}"

        #formata os dados brutos da API para formato amigavel
        voos_formatados = formatar_voo(voos)
        #Se não encontrou voos ou houve erro na formatação, retorna mensagem de erro
        if not voos_formatados or (isinstance(voos_formatados, list) and voos_formatados[0].get("erro")):
            return "ERRO_FERRAMENTA: Nenhuma passagem encontrada que corresponda aos critérios."

        # Monta a resposta em texto com as informações de cada voo encontrado
        resposta = []
        for i, voo in enumerate(voos_formatados):
            resposta.append(
                f"Voo {i+1}: Companhia: {voo.get('companhia', 'N/A')}, "
                f"Aeronave: {voo.get('aeronave', 'N/A')}, "
                f"Origem: {voo.get('origem', 'N/A')}, Destino: {voo.get('destino', 'N/A')}, "
                f"Partida: {voo.get('partida', 'N/A')}, Chegada: {voo.get('chegada', 'N/A')}, "
                f"Duração: {voo.get('duracao', 'N/A')}, Escalas: {voo.get('escalas', 'N/A')}, "
                f"Preço: {voo.get('moeda', '')} {voo.get('preco', 'N/A')}"
            )
        
        if not resposta:
            return "ERRO_FERRAMENTA: Não consegui formatar nenhuma resposta. Tente novamente."
        # Junta todas as linhas da resposta em uma string única
        resposta_str = "\n".join(resposta).strip()

        if not resposta_str:
            return "ERRO_FERRAMENTA Nenhum resultado válido foi formatado."
        
        # Retorna a string final com as opções de voos formatadas
        print(f"DEBUG: resposta string final da api:{resposta_str}")
        return resposta_str
        #return {"resultado": resposta_str}
    except Exception as e:
        return "resultado: ERRO_FERRAMENTA: Erro ao processar data: {str(e)}"


      