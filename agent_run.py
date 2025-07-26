from utils.formatters import deve_buscar_passagem
import json
import traceback

def executar_agente(entrada, usuario, agente_passagens):
    #print("DEBUG: executar_agente foi chamada com entrada:", entrada)
    
    # --- Verificação inicial reforçada ---
    #verifica se o agente está configurado corretamente e se os dados do usuario são validos
    if not all([
        agente_passagens,
        hasattr(agente_passagens, 'invoke'),
        isinstance(usuario.dadosviagem, dict)
    ]):
        print("ERRO: Configuração do agente ou dados inválidos")
        return False

    # --- Validação dos dados obrigatórios ---
    dados_viagem = usuario.dadosviagem
    campos_obrigatorios = ["origem", "destino", "dia"]
    
    if not all(dados_viagem.get(campo) for campo in campos_obrigatorios):
        print("MOCHI: ❌ Faltam informações essenciais (origem, destino ou data)")
        return False

    # --- Formatação robusta do input ---
    try: #estrutura os dados para o agente 
        input_agente = {
            "viagem": {
                "origem": dados_viagem["origem"],
                "destino": dados_viagem["destino"],
                "data": dados_viagem["dia"],
            },
            "instrucao": "Busque passagens aéreas com base nos dados fornecidos"
        }
        
        # Conversão para JSON string com tratamento de caracteres
        input_str = json.dumps(input_agente, ensure_ascii=False)
        #print(type(f"DEBUG: Input formatado para o agente:\n{input_str}"))

        # --- Chamada protegida ao agente : tratamento de exceções---
        try:
            resultado = agente_passagens.invoke({"input": input_str}) #invoca o agente principal passando o input
            if resultado is None or resultado == "":
                return "ERRO: Nenhum conteúdo retornado."

            #output é o formato padrão de retorno do langchain Agents -string
            output = resultado.get("output", "").strip() #extrai e limpa a resposta do agente
            #valida se a resposta não está vazia
            if not output:
                raise ValueError("Resposta vazia do agente")

            #print(f"DEBUG: Resposta completa do agente:\n{resultado}")
            
            # --- Análise da resposta ---
            if "erro" in output.lower():
                print(f"BOT: ⚠️ Problema na busca: {output}")
                return False
            #se sucesso: exibe   
            #print(f"MOCHI: ✈️ Opções encontradas:\n{output}")
            return output

        except Exception as e:
            print(f"ERRO NA CHAMADA: {str(e)}")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"ERRO NA FORMATAÇÃO: {str(e)}")
        return False