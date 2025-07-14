import re

PADRAO_FINALIDADE = r"(?:viagem\s+)?(?:a\s+trabalho|de\s+lazer|trabalho|lazer)"

def atualizar_dados_usuario(entrada: str, usuario):
    dados_usuario = usuario.preferencias
    # Em regex.py, dentro de atualizar_dados_usuario
    # Garante que todas as chaves estão presentes
    default_user_preferences = {
        "origem": None, "destino": None, "dia": None,
        "finalidade": None, "preferencias": [], "restricoes": []
    }

    if not dados_usuario:
        usuario.preferencias = default_user_preferences.copy()
    else:
        for key, default_value in default_user_preferences.items():
            if key not in dados_usuario:
                dados_usuario[key] = default_value
            elif isinstance(default_value, list) and not isinstance(dados_usuario[key], list):
                dados_usuario[key] = []

    match_name = re.search(r"(?:meu nome é|eu sou|pode me chamar de|sou)\s+([a-zA-ZÀ-ÿ\s]+)", entrada.lower())
    if match_name:
        nome_extraido = match_name.group(1).strip().title()
        if not hasattr(usuario, 'nome') or usuario.nome != nome_extraido:
            usuario.nome = nome_extraido
            print(f"DEBUG: Nome do usuário atualizado para '{usuario.nome}'")

    # Dia
    match_dia = re.search(r"(?:dia|em)\s+(\d{1,2}(?:\s+de\s+[a-zA-Zà-ú]+){1,2}(?:\s+de\s+\d{4})?)", entrada.lower())
    if match_dia:
        dados_usuario["dia"] = match_dia.group(1).strip()
        print(f"DEBUG: Dia atualizado para '{dados_usuario['dia']}'")

    # Destino
    match_destino = re.search(r"(?:para|destino é)\s+([a-zA-ZÀ-ÿ\s]+)", entrada.lower())
    if match_destino:
        destino = match_destino.group(1).strip().title()
        if len(destino.split()) <= 4:
            dados_usuario["destino"] = destino
            print(f"DEBUG: Destino atualizado para '{dados_usuario['destino']}'")

    # Origem
    match_origem = re.search(
        r"(?:de|partindo de|origem é)\s+([a-zA-ZÀ-ÿ\s]+?)(?:\s*,\s*para|\s*,\s*dia|\s*em|\s*no dia|\s*\Z)",
        entrada.lower()
    )
    if match_origem:
        origem = match_origem.group(1).strip().title()
        if len(origem.split()) <= 4:
            dados_usuario["origem"] = origem
            print(f"DEBUG: Origem atualizada para '{dados_usuario['origem']}'")
    elif not dados_usuario["origem"] and re.match(r"^([a-zA-ZÀ-ÿ\s]+?),\s*(?:dia|em|para)", entrada.lower()):
        origem = re.match(r"^([a-zA-ZÀ-ÿ\s]+?),\s*(?:dia|em|para)", entrada.lower()).group(1).strip().title()
        if len(origem.split()) <= 4 and origem:
            dados_usuario["origem"] = origem
            print(f"DEBUG: Origem atualizada (início da frase) para '{dados_usuario['origem']}'")
   
    # Preferência de clima
    if "frio" in entrada.lower() and "gosta de clima frio" not in dados_usuario["preferencias"]:
        dados_usuario["preferencias"].append("gosta de clima frio")
        print(f"DEBUG: Preferência 'gosta de clima frio' adicionada.")
    
    #finalidade de viagem
    match_finalidade = re.search(PADRAO_FINALIDADE, entrada.lower())
    if match_finalidade:
        finalidade_extraida = match_finalidade.group(0)
        if "trabalho" in finalidade_extraida:
            dados_usuario['finalidade'] = "trabalho"
        elif "lazer" in finalidade_extraida:
            dados_usuario['finalidade'] = "lazer"
        print(f"DEBUG: Finalidade atualizada para '{dados_usuario['finalidade']}'")

    return dados_usuario