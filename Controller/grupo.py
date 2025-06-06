from flask import Blueprint, jsonify
from Model.grupo import *

Grupo_Blueprint = Blueprint('grupo', __name__)

@Grupo_Blueprint.route('/', methods=["GET"])
def get_grupos():
    grupos = ListarGrupos()
    return jsonify([g.dici() for g in grupos])

@Grupo_Blueprint.route('/<int:id>', methods=["GET"])
def get_grupo_por_nome(id):
    grupo = ListarGrupoPorId(id)
    if not grupo:
        return jsonify({"erro": "Grupo não encontrado"}), 404
    return jsonify(grupo.dici())

@Grupo_Blueprint.route('/', methods=["POST"])
def create_grupo():
    dados = request.get_json()
    novo, erro = CriarGrupo(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify(novo.dici()), 201

@Grupo_Blueprint.route('/<int:id>', methods=["PUT"])
def update_grupo(id):
    dados = request.get_json()
    atualizado, erro = AtualizarGrupo(id, dados)
    if erro:
        return jsonify({"erro": erro}), 404
    return jsonify(atualizado.dici())

@Grupo_Blueprint.route('/<int:id>', methods=["DELETE"])
def delete_grupo(id):
    sucesso, erro = DeletarGrupo(id)
    if not sucesso:
        return jsonify({"erro": erro}), 404
    return jsonify({"mensagem": "Grupo deletado com sucesso"})