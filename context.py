# Importa a função textwrap.dedent, que remove indentação comum em blocos de texto
import textwrap
from datetime import datetime

def construir_contexto(usuario, entrada):
    #garante q dados seja sempre um dicionario
    dados = usuario.dadosviagem or {} # Recupera os dados da viagem do usuário (ou dicionário vazio)
    finalidade = usuario.finalidade  # Finalidade da viagem (trabalho/lazer ou None)
    preferencias = usuario.preferencias or {} # Preferências do usuário, como clima ou lugares
    
    passagens = getattr(usuario, 'passagens', {})
    passagens_formatadas = []

    if isinstance(passagens, dict):
        for busca_id, detalhes in passagens.items():
            try:
                if isinstance(detalhes, dict):
                    # Formatação para dicionário estruturado
                    voos = detalhes.get('voos', []) if isinstance(detalhes.get('voos'), list) else []
                    if isinstance(voos, list):
                        info_voos = [
                            f"  ✈️ {i}. {voo.get('cia', 'Companhia')} "
                            f"| ⏱️ {voo.get('horario', '--:--')} "
                            f"| 💰 {voo.get('preco', '?')} "
                            f"| 🛑 {voo.get('escalas', '?')} escalas"
                            for i, voo in enumerate(voos, 1)
                        ]
                        passagens_formatadas.append(
                            f"\n🔍 Busca {busca_id}:\n" + 
                            "\n".join(info_voos) +
                            (f"\n⭐ Melhor: {detalhes.get('melhor_opcao', {}).get('cia', 'N/A')}" 
                            if isinstance(detalhes.get('melhor_opcao'), dict) else "")
                    )
            except Exception as e:
                print(f"⚠️ Erro ao formatar passagem {busca_id}: {str(e)}")
                continue


    contexto = f"""
    Nome: {usuario.nome or 'não informado'}
    Origem: {dados.get('origem') or 'não informado'}
    Destino: {dados.get('destino') or 'não informado'}
    Dia: {dados.get('dia') or 'não informado'}
    Finalidade: {usuario.finalidade or 'não informado'}
    Preferências: {', '.join([f"{k}: {v}" for k, v in preferencias.items() if v]) or 'não informado'}
    ✈️ Histórico de Buscas: {''.join(passagens_formatadas) if passagens_formatadas else 'Nenhuma busca salva'}
    
    Usuário diz: {entrada}
    """
    return textwrap.dedent(contexto).strip() # Remove espaçamentos/indentação do bloco de texto e retorna como string limpa
