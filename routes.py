# routes.py

from flask import request, jsonify
from tools.viagens_api import buscar_passagens
from api.formatador import formatar_voo

def registrar_rotas(app):
    @app.route("/")
    def home():
        return "Chatbot SkIA está funcionando via web!"

    @app.route("/api/voos", methods=["GET"])
    def voos():
        origem = request.args.get("origem")
        destino = request.args.get("destino")
        data = request.args.get("data")

        if not all([origem, destino, data]):
            return jsonify({"erro": "Parâmetros 'origem', 'destino' e 'data' são obrigatórios."}), 400

        print(f"DEBUG: Recebido no Flask: origem={origem}, destino={destino}, data={data}")
        # Sua lógica ou chamada para função externa buscar_voos()
        resultado = buscar_passagens(origem, destino, data)

        if isinstance(resultado, str) and resultado.startswith("ERRO_FERRAMENTA:"):
            print(f"ERRO: Erro retornado pela ferramenta: {resultado}")
            return jsonify({"erro": resultado}), 500
        try:
            resultado_filtrado = formatar_voo(resultado)
            formatted_output_for_llm = []
            if resultado_filtrado:
                for i, voo_info in enumerate(resultado_filtrado):
                    formatted_output_for_llm.append(
                         f"Voo {i+1}: Companhia: {voo_info.get('companhia', 'N/A')}, "
                    f"Origem: {voo_info.get('origem', 'N/A')}, Destino: {voo_info.get('destino', 'N/A')}, "
                    f"Partida: {voo_info.get('partida', 'N/A')}, Chegada: {voo_info.get('chegada', 'N/A')}, "
                    f"Duração: {voo_info.get('duracao', 'N/A')}, Escalas: {voo_info.get('escalas', 'N/A')}, "
                    f"Preço: {voo_info.get('moeda', '')} {voo_info.get('preco', 'N/A')}"
                    )
                final_llm_output = "\n".join(formatted_output_for_llm)
            else:
                final_llm_output = "Nenhuma passagem encontrada que corresponda aos critérios."

            return final_llm_output , 200
        except Exception as e:
            print(f"ERRO: Erro ao formatar os voos: {str(e)}")
            return jsonify({"erro": f"Erro interno ao formatar resultados: {str(e)}"}), 500

       