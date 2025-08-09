#código antigo que era somente a API Amadeus
#usado o formatar_voo()

from datetime import datetime
# Mapeamento de códigos de companhias aéreas para nomes completos
MAPEAMENTO_COMPANHIAS = {
    "G3": "Gol",
    "LA": "LATAM",
    "JJ": "LATAM Brasil",
    "TP": "TAP Portugal",
    "AD": "Azul",
    "AZ": "ITA Airways",
    "AF": "Air France",
    "KL": "KLM",
    "LX": "Swiss",
    "BA": "British Airways",
    "AA": "American Airlines",
    "DL": "Delta",
    "UA": "United",
    "EK": "Emirates",
    "QR": "Qatar Airways",
    "EY": "Etihad",
    "LH": "Lufthansa",
    "IB": "Iberia",
    "AY": "Finnair",
    "QF": "Qantas",
    "SA": "South African",
    "NZ": "Air New Zealand",
    "SQ": "Singapore Airlines",
    "CX": "Cathay Pacific",
    "NH": "ANA",
    "JL": "JAL",
    "KE": "Korean Air",
    "OZ": "Asiana",
    "CI": "China Airlines",
    "BR": "EVA Air",
    "TG": "Thai Airways",
    "VN": "Vietnam Airlines",
    "GA": "Garuda Indonesia",
    "MH": "Malaysia Airlines"
}

MAPEAMENTO_AERONAVES = {
    # Airbus
    "318": "Airbus A318",
    "319": "Airbus A319",
    "320": "Airbus A320",
    "321": "Airbus A321",
    "32N": "Airbus A320neo",
    "32Q": "Airbus A321neo",
    "332": "Airbus A330-200",
    "333": "Airbus A330-300",
    "359": "Airbus A350-900",
    "351": "Airbus A350-1000",
    "388": "Airbus A380-800",
    
    # Boeing
    "736": "Boeing 737-600",
    "73G": "Boeing 737-700",
    "738": "Boeing 737-800",
    "739": "Boeing 737-900",
    "37M": "Boeing 737 MAX 8",
    "37L": "Boeing 737 MAX 9",
    "37K": "Boeing 737 MAX 10",
    "788": "Boeing 787-8",
    "789": "Boeing 787-9",
    "781": "Boeing 787-10",
    "772": "Boeing 777-200",
    "77W": "Boeing 777-300ER",
    
    # Embraer
    "E70": "Embraer E170",
    "E75": "Embraer E175",
    "E90": "Embraer E190",
    "E95": "Embraer E195",
    "290": "Embraer E190-E2",  # Código alternativo
    "295": "Embraer E195-E2",  # Código alternativo
    "E290": "Embraer E190-E2",
    "E295": "Embraer E195-E2",
    
    # Bombardier
    "CRJ": "Bombardier CRJ200",
    "CR7": "Bombardier CRJ700",
    "CR9": "Bombardier CRJ900",
    "CRK": "Bombardier CRJ1000",
    
    # ATR
    "AT4": "ATR 42-600",
    "AT7": "ATR 72-600",
    
    # Outros
    "SU9": "Sukhoi Superjet 100",
    "CS3": "Airbus A220-300"
}

def formatar_aeronave(codigo, companhia=None): #retorna o nome do modelo da aeronave a partir do código.
    if not codigo or codigo == "N/A":
        return "Modelo não especificado"
    
    # Tenta encontrar no mapeamento
    modelo = MAPEAMENTO_AERONAVES.get(codigo)
    
    # Se não encontrado, monta um nome genérico
    if not modelo:
        if codigo.startswith('7'):  # Boeing (7x7)
            modelo = f"Boeing {codigo}"
        elif codigo.startswith('3'):  # Airbus (3xx)
            modelo = f"Airbus {codigo}"
        elif codigo.startswith('E') or codigo.startswith('2'):  # Embraer (E-Jets ou E2)
            modelo = f"Embraer {codigo}"
        else:
            modelo = codigo
             
    return modelo

def formatar_companhia(codigo):
    """Formata o código da companhia aérea para o nome completo"""
    return MAPEAMENTO_COMPANHIAS.get(codigo, codigo)  # Retorna o código se não encontrar no mapeamento

def formatar_voo(voos_data: list) -> list: #funçao usada para formatar os voos.
    voos_formatados = []
    if not isinstance(voos_data, list): #verifica se a entrada é uma lista
        print(f"ERRO_FORMATADOR: Entrada inesperada para formatar_voo. Esperado lista, recebido: {type(voos_data)} - {voos_data}")
        # Retorna uma mensagem de erro que pode ser usada pelo chatbot
        return [{"erro": "Erro interno ao formatar dados de voo: formato inesperado."}]


    for idx, voo in enumerate(voos_data):
        try:
            # Garante que 'voo' é um dicionário antes de tentar acessar chaves
            if not isinstance(voo, dict):
                print(f"WARNING_FORMATADOR: Item de voo inesperado na lista (não é um dicionário) no índice {idx}: {voo}")
                voos_formatados.append({"erro": f"Erro ao formatar voo {idx+1}: item inválido."})
                continue # Pula para o próximo item

            # Acessa itinerários e segmentos com get() para evitar KeyError
            itinerario = voo.get("itineraries", [None])[0]
            if not itinerario:
                print(f"WARNING_FORMATADOR: Itinerário ausente para voo no índice {idx}. Voo: {voo}")
                voos_formatados.append({"erro": f"Erro ao formatar voo {idx+1}: itinerário não encontrado."})
                continue

            segmentos = itinerario.get("segments")
            if not segmentos or len(segmentos) == 0:
                print(f"WARNING_FORMATADOR: Segmentos ausentes para voo no índice {idx}. Voo: {voo}")
                voos_formatados.append({"erro": f"Erro ao formatar voo {idx+1}: segmentos de voo não encontrados."})
                continue
            #infos basicas dos voos
            primeiro_segmento = segmentos[0]
            ultimo_segmento = segmentos[-1]

            # Usando .get() para chaves que podem não estar sempre presentes, com valor padrão
            codigo_companhia = primeiro_segmento.get("carrierCode", "N/A")
            companhia = formatar_companhia(codigo_companhia)

            # Acesso seguro para aircraft.code
            codigo_aeronave = primeiro_segmento.get("aircraft", {}).get("code", "N/A")
            aeronave = formatar_aeronave(codigo_aeronave)

            assentos = voo.get("numberOfBookableSeats", "N/A")

            # Acesso seguro para departure/arrival.at
            partida_at = primeiro_segmento.get("departure", {}).get("at")
            chegada_at = ultimo_segmento.get("arrival", {}).get("at")

            partida = datetime.fromisoformat(partida_at).strftime("%H:%M") if partida_at else "N/A"
            chegada = datetime.fromisoformat(chegada_at).strftime("%H:%M") if chegada_at else "N/A"
            
            origem = primeiro_segmento.get("departure", {}).get("iataCode", "N/A")
            destino = ultimo_segmento.get("arrival", {}).get("iataCode", "N/A")

            duracao_iso = itinerario.get("duration", "N/A")
            duracao = duracao_iso.replace("PT", "").lower().replace("h", "h").replace("m", "m") if duracao_iso != "N/A" else "N/A"
            #quantidade de escalas
            escalas = len(segmentos) - 1
            if escalas == 0:
                texto_escalas = "Direto"
            elif escalas == 1:
                texto_escalas = "1 escala"
            else:
                texto_escalas = f"{escalas} escalas"

            preco = voo.get("price", {}).get("total", "N/A")
            moeda = voo.get("price", {}).get("currency", "BRL") # Moeda padrão BRL

            voos_formatados.append({
                "companhia": companhia,
                "aeronave": aeronave,
                "assentosDisponiveis": assentos,
                "partida": partida,
                "chegada": chegada,
                "origem": origem,
                "destino": destino,
                "duracao": duracao,
                "escalas": texto_escalas,
                "preco": float(preco) if isinstance(preco, (int, float, str)) and str(preco).replace('.', '', 1).isdigit() else "N/A", # Converte para float com segurança
                "moeda": moeda
            })

        except Exception as e:
            # Captura qualquer outro erro inesperado durante a formatação de um voo específico
            print(f"ERRO_FORMATADOR: Erro ao processar voo no índice {idx}: {e}. Dados do voo: {voo}")
            voos_formatados.append({"erro": f"Não foi possível formatar detalhes do voo {idx+1}."})

    return voos_formatados
