def construir_contexto(usuario, entrada):
    dados = usuario.preferencias or {}
    return f"""
    Origem: {dados.get('origem') or 'não informado'}
    Destino: {dados.get('destino') or 'não informado'}
    Data: {dados.get('dia') or 'não informado'}
    Tipo de viagem: {dados.get('viagem') or 'não informado'}
    Preferências: {', '.join(dados.get('preferencias', [])) or 'não informado'}
    
    Usuário diz: {entrada}
    """
