def deve_buscar_passagem(texto):
    termos = ["buscar", "passagem", "preço", "voo", "quanto custa", "passagens", "voos"]
    return any(p in texto.lower() for p in termos)

entrada = "quero buscar passagens para São Paulo"

print("DEBUG: deve_buscar_passagem:", deve_buscar_passagem(entrada))