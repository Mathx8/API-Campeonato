from flask import Flask, redirect, request
from config import db, Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from Controller.jogador import Jogador_Blueprint
from Controller.partida import Partida_Blueprint
from Controller.time import Time_Blueprint
from Controller.competicao import Competicao_Blueprint
from Controller.grupo import Grupo_Blueprint
from Controller.backup import Backup_Blueprint
from swagger.swagger_config import configure_swagger

app = Flask(__name__)
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }
     })

@app.before_request
def enforce_https():
    """Redirecionamento inteligente para HTTPS"""
    if not request.is_secure:
        if 'X-Forwarded-Proto' in request.headers:
            if request.headers['X-Forwarded-Proto'] == 'http':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
        else:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

configure_swagger(app)
'''app.register_blueprint(Jogador_Blueprint, url_prefix="/jogador")
app.register_blueprint(Partida_Blueprint, url_prefix="/partida")
app.register_blueprint(Time_Blueprint, url_prefix="/time")
app.register_blueprint(Competicao_Blueprint, url_prefix="/competicao")
app.register_blueprint(Grupo_Blueprint, url_prefix="/grupo")
app.register_blueprint(Backup_Blueprint, url_prefix="/backup")'''

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
