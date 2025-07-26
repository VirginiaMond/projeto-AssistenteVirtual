import re

PADRAO_FINALIDADE = r"(?:viagem\s+)?(a\s+trabalho|de\s+lazer|trabalho|lazer)"
#---função principal que atualiza os dados do usuário com base na entrada de texto
def atualizar_dados_usuario(entrada: str, usuario):
    dados_usuario = usuario.dadosviagem #acesso ao dicionario
    
    # Garante que todas as chaves estão presentes
    default_user_dados = {
        "origem": None, 
        "destino": None, 
        "dia": None
    }
    # se nao possuir dados, cria
    if not dados_usuario:
        usuario.dadosviagem = default_user_dados.copy()
    else:
        #para cada chave esperada, verifica se está presente e válida
        for key, default_value in default_user_dados.items():
            if key not in dados_usuario:
                dados_usuario[key] = default_value
            #corrige caso uma chave que deveria ser lista venha diferente
            elif isinstance(default_value, list) and not isinstance(dados_usuario[key], list):
                dados_usuario[key] = []
    #processamento do nome (extração)
    match_name = re.search(r"(?:meu nome é|eu sou|pode me chamar de|sou)\s+([a-zA-ZÀ-ÿ\s]+)", entrada.lower())
    if match_name:
        nome_extraido = match_name.group(1).strip().title()
        if not hasattr(usuario, 'nome') or usuario.nome != nome_extraido:
            usuario.nome = nome_extraido
            #print(f"DEBUG: Nome do usuário atualizado para '{usuario.nome}'")

    # Dia/data
    match_dia = re.search(r"(?:dia|data|em)\s+(\d{1,2}(?:\s+de\s+[a-zA-Zà-ú]+){1,2}(?:\s+de\s+\d{4})?)", entrada.lower())
    if match_dia:
        dados_usuario["dia"] = match_dia.group(1).strip()
        #print(f"DEBUG: Dia atualizado para '{dados_usuario['dia']}'")

    # Destino
    match_destino = re.search(r"(?:para|destino é)\s+([a-zA-ZÀ-ÿ\s]+)", entrada.lower())
    if match_destino:
        destino = match_destino.group(1).strip().title()
        if len(destino.split()) <= 4:
            dados_usuario["destino"] = destino
            #print(f"DEBUG: Destino atualizado para '{dados_usuario['destino']}'")

    # Origem
    match_origem = re.search(
        r"(?:de|partindo de|origem é)\s+([a-zA-ZÀ-ÿ\s]+?)(?:\s*,\s*para|\s*,\s*dia|\s*em|\s*no dia|\s*\Z)",
        entrada.lower()
    )
    if match_origem:
        origem = match_origem.group(1).strip().title()
        if len(origem.split()) <= 4:
            dados_usuario["origem"] = origem
            #print(f"DEBUG: Origem atualizada para '{dados_usuario['origem']}'")
    #caso origem esteja no inicio da frase
    elif not dados_usuario["origem"] and re.match(r"^([a-zA-ZÀ-ÿ\s]+?),\s*(?:dia|em|para)", entrada.lower()):
        origem = re.match(r"^([a-zA-ZÀ-ÿ\s]+?),\s*(?:dia|em|para)", entrada.lower()).group(1).strip().title()
        if len(origem.split()) <= 4 and origem:
            dados_usuario["origem"] = origem
            #print(f"DEBUG: Origem atualizada (início da frase) para '{dados_usuario['origem']}'")
    
    #finalidade de viagem
    match_finalidade = re.search(PADRAO_FINALIDADE, entrada.lower())
    if match_finalidade:
        finalidade_extraida = match_finalidade.group(1).lower()
        
        if "trabalho" in finalidade_extraida:
            usuario.finalidade = "trabalho"
        elif "lazer" in finalidade_extraida:
            usuario.finalidade = "lazer"
        #print(f"DEBUG: Finalidade extraída: '{finalidade_extraida}', Definida como: '{usuario.finalidade}'")

    return dados_usuario