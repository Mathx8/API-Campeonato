from flask import Flask, redirect, request
from config import db, Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from Controller.jogador import Jogador_Blueprint
from Controller.partida import Partida_Blueprint
from Controller.time import Time_Blueprint
from Controller.competicao import Competicao_Blueprint
from Controller.grupo import Grupo_Blueprint
from swagger.swagger_config import configure_swagger

app = Flask(__name__)
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000"],
             "supports_credentials": True,
             "always_send": True
         }
     })

@app.before_request
def enforce_https():
    """Redirecionamento HTTPS inteligente para o Render"""
    if request.method == "OPTIONS":
        return
    
    is_https = (
        request.is_secure or 
        request.headers.get('X-Forwarded-Proto', 'https') == 'https'
    )
    if not is_https and 'localhost' not in request.host:
        https_url = request.url.replace('http://', 'https://', 1)
        return redirect(https_url, code=301)
    
@app.after_request
def add_cors_headers(response):
    """Garante headers CORS em todas as respostas"""
    if request.method == "OPTIONS":
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '600'
    return response

app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

configure_swagger(app)
app.register_blueprint(Jogador_Blueprint, url_prefix="/jogador")
app.register_blueprint(Partida_Blueprint, url_prefix="/partida")
app.register_blueprint(Time_Blueprint, url_prefix="/time")
app.register_blueprint(Competicao_Blueprint, url_prefix="/competicao")
app.register_blueprint(Grupo_Blueprint, url_prefix="/grupo")

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        threaded=True
    )
