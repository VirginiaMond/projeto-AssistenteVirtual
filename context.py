import textwrap

def construir_contexto(usuario, entrada):
    dados = usuario.preferencias or {}
    contexto = f"""
    Origem: {dados.get('origem') or 'não informado'}
    Destino: {dados.get('destino') or 'não informado'}
    Data: {dados.get('dia') or 'não informado'}
    Finalidade da viagem: {dados.get('finalidade') or 'não informado'}
    Preferências: {', '.join(dados.get('preferencias', [])) or 'não informado'}
    
    Usuário diz: {entrada}
    """
    return textwrap.dedent(contexto).strip()
