#def deve_buscar_passagem(texto):
 #   termos = ["buscar", "passagem", "preço", "voo", "quanto custa", "passagens", "voos"]
  #  return any(p in texto.lower() for p in termos)

#entrada = "quero buscar passagens para São Paulo"

#print("DEBUG: deve_buscar_passagem:", deve_buscar_passagem(entrada))

import re

def deve_buscar_passagem(texto: str) -> bool:
    texto = texto.lower()

    # Expressões que combinam ações e objeto (voo ou passagem)
    padroes = [
        r"\b(buscar|comprar|reservar|procurar|achar|saber|ver)\b.*\b(passagens?|voos?)\b",  # buscar passagens
        r"\b(passagens?|voos?)\b.*\b(disponivel|tem)\b",  
        r"\b(desejo|preciso)\b.*\b(passagens?|voos?)\b",  # quero passagens
    ]

    return any(re.search(p, texto) for p in padroes)


