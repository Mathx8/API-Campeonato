from . import api
from swagger.namespace.jogador_namespace import jogador_ns
from swagger.namespace.time_namespace import time_ns
from swagger.namespace.partida_namespace import partida_ns
from swagger.namespace.competicao_namespace import competicao_ns
from swagger.namespace.grupo_namespace import grupo_ns
from swagger.namespace.backup_namespace import backup_ns

def configure_swagger(app):
    api.init_app(app)
    
    api.add_namespace(jogador_ns, path="/jogador")
    api.add_namespace(time_ns, path="/time")
    api.add_namespace(competicao_ns, path="/competicao")
    api.add_namespace(grupo_ns, path="/grupo")
    api.add_namespace(partida_ns, path="/partida")
    api.add_namespace(backup_ns, path="/backup")
    
    api.mask_swagger = False