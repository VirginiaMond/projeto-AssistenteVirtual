# Importa a função textwrap.dedent, que remove indentação comum em blocos de texto
import textwrap

def construir_contexto(usuario, entrada):
    #garante q dados seja sempre um dicionario
    dados = usuario.dadosviagem or {} # Recupera os dados da viagem do usuário (ou dicionário vazio)
    finalidade = usuario.finalidade  # Finalidade da viagem (trabalho/lazer ou None)
    preferencias = usuario.preferencias or {} # Preferências do usuário, como clima ou lugares

    contexto = f"""
    Origem: {dados.get('origem') or 'não informado'}
    Destino: {dados.get('destino') or 'não informado'}
    Dia: {dados.get('dia') or 'não informado'}
    Finalidade: {usuario.finalidade or 'não informado'}
    Preferências: {', '.join([f"{k}: {v}" for k, v in preferencias.items() if v]) or 'não informado'}

    Usuário diz: {entrada}
    """
    return textwrap.dedent(contexto).strip() # Remove espaçamentos/indentação do bloco de texto e retorna como string limpa
