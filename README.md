# projeto- Assistente Virtual de Viagens
Criação de assistente Virtual de viagens com interface conversacional (Chatbot) destinado ao meu TCC/ BICT via terminal


## Descrição  
Aplicação em Python que utiliza LangChain e Google GenAI para rodar no terminal (linha de comando), consumindo APIs via requests.

## Requisitos - instalação

- Python 3.8 ou superior

1. Clone o repositório:  
````
   * no bash
   git clone <https://github.com/VirginiaMond/projeto-chatbot.git>
   cd <projeto-chatbot>
   ````

2. Crie e ative um ambiente virtual, respectivamente:

   ```
   * no powershell
   python -m venv venv

   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

4. Configure o arquivo `.env` com suas variáveis na pasta raiz:

   ```
   GOOGLE_API_KEY=sua_key_aqui
   ```
   Na pasta api, crie outro `.env` com as suas variáveis (key) da API Amadeus:
   ```
   AMADEUS_CLIENT_ID=sua_key_ID_aqui
   AMADEUS_CLIENT_SECRET=sua_key_secret_aqui 
   ```
## Como rodar

Execute o script Python principal no terminal:

```
python main.py
```

## Pacotes usados

* `langchain`: integração com modelos de linguagem.
* `langchain-google-genai`: plugin para usar Google GenAI no LangChain.
* `python-dotenv`: gerencia variáveis de ambiente a partir do arquivo `.env`.
* `...´

---

