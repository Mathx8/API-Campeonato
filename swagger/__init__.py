from flask_restx import Api

api = Api(
    version="1.0",
    title="API de Campeonato",
    description="Documentação da API para Jogador, Time, Competição, Grupo, Partida e Backup",
    doc="/", 
    mask_swagger=False,
)