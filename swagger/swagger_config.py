from . import api
from swagger.namespace.jogador_namespace import jogador_ns
from swagger.namespace.time_namespace import time_ns
from swagger.namespace.partida_namespace import partida_ns
from swagger.namespace.competicao_namespace import competicao_ns
from swagger.namespace.grupo_namespace import grupo_ns
from swagger.namespace.auth_namespace import api as auth_ns
from swagger.namespace.premiacao_namespace import premiacao_ns
from swagger.namespace.sumula_namespace import sumula_ns
from swagger.namespace.selecao_namespace import selecao_ns

def configure_swagger(app):
    api.init_app(app)
    
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(jogador_ns, path="/jogador")
    api.add_namespace(competicao_ns, path="/competicao")
    api.add_namespace(grupo_ns, path="/grupo")
    api.add_namespace(time_ns, path="/time")
    api.add_namespace(partida_ns, path="/partida")
    api.add_namespace(sumula_ns, path="/sumula")
    api.add_namespace(selecao_ns, path="/selecao")
    api.add_namespace(premiacao_ns, path="/premiacao")
    
    api.mask_swagger = False