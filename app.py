from flask import Flask
from routes import registrar_rotas 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

registrar_rotas(app)

if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=False, use_reloader=False,port=5000)