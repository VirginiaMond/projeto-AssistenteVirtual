from datetime import datetime
import locale
from api.amadeus_client import buscar_voos
from api.formatador import formatar_voo


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


def completar_ano_se_faltando(data_str: str) -> str:
    """Adiciona o ano atual à string de data se ela não contiver ano."""
    if any(str(ano) in data_str for ano in range(2023, 2031)):  # já tem ano
        return data_str
    ano_atual = datetime.now().year
    return f"{data_str} de {ano_atual}"

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

def corrigir_data(data):
    partes = data.lower().split()
    for i, palavra in enumerate(partes):
        if palavra not in ['de', 'do', 'da', 'e']:
            partes[i] = palavra.capitalize()
    return ' '.join(partes)

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

        data_corrigida = corrigir_data(data.strip())
        data_corrigida = completar_ano_se_faltando(data_corrigida)
        print(f"DEBUG: Data corrigida para parses: '{data_corrigida}'")

        formatos = ["%d de %B de %Y", "%d/%m/%Y", "%Y-%m-%d"]
        data_formatada = None

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

        if isinstance(voos, dict) and ("api_error" in voos or "api_status" in voos):
            return f"ERRO_FERRAMENTA: Erro ao consultar a API: {voos.get('api_error') or voos.get('api_status')}"


        voos_formatados = formatar_voo(voos)

        if not voos_formatados or (isinstance(voos_formatados, list) and voos_formatados[0].get("erro")):
            return "ERRO_FERRAMENTA: Nenhuma passagem encontrada que corresponda aos critérios."

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

        return "\n".join(resposta)
        
    except Exception as e:
        return f"ERRO_FERRAMENTA: Erro ao processar data: {str(e)}"


      