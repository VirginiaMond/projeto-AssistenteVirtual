from utils.formatters import deve_buscar_passagem

def executar_agente(entrada, usuario, agente_passagens):
    print("DEBUG: executar_agente foi chamada com entrada:", entrada)
    # 1. Verifica se o texto sugere busca
    if not deve_buscar_passagem(entrada):
        return False

    dados = usuario.preferencias
    print("\nBOT (buscando passagens):")

    # 2. Monta input com base nos dados conhecidos (origem, destino, data)
    partes = []
    if dados.get("origem"):
        partes.append(f"Origem: {dados['origem']}")
    if dados.get("destino"):
        partes.append(f"Destino: {dados['destino']}")
    if dados.get("dia"):
        partes.append(f"Data: {dados['dia']}")

    # Se nenhum dado está presente, não adianta tentar
    if not partes:
        print("BOT: Ainda não tenho informações suficientes para buscar as passagens.")
        return False

    agent_input = " ".join(partes)
    print(f"DEBUG: Input para o agente: '{agent_input}'")

    try:
        resultado = agente_passagens.invoke({"input": agent_input})
        output = resultado.get('output', str(resultado)).strip()

        print(f"DEBUG resultado bruto do agente: {resultado}")
        print(f"DEBUG output extraído: '{output}'")

        if not output:
            output = "Desculpe, não encontrei resultados para sua busca."

        if output == "INFORMACOES_INSUFICIENTES":
            print("BOT: Ainda faltam informações essenciais (origem, destino ou data).")
            return False

        if output.startswith("ERRO_BUSCA_PASSAGENS:"):
            erro_msg = output.replace("ERRO_BUSCA_PASSAGENS:", "").strip()
            print("BOT: Ocorreu um erro ao buscar passagens:", erro_msg)
            return False

        # Caso a resposta seja válida
        print("BOT:", output)
        return True

    except Exception as e:
        print(f"BOT: Erro inesperado ao acionar o agente: {str(e)}")
        return False