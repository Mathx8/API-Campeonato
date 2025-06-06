from flask import Blueprint, jsonify
from Model.competicao import *

Competicao_Blueprint = Blueprint('competicao', __name__)

@Competicao_Blueprint.route('/', methods=["GET"])
def get_competicoes():
    competicoes = ListarCompeticoes()
    return jsonify([c.dici() for c in competicoes])

@Competicao_Blueprint.route('/<int:id>', methods=["GET"])
def get_competicao_por_nome(id):
    competicao = ListarCompeticaoPorId(id)
    if not competicao:
        return jsonify({"erro": "Competição não encontrada"}), 404
    return jsonify(competicao.dici())

@Competicao_Blueprint.route('/', methods=["POST"])
def create_competicao():
    dados = request.get_json()
    novo, erro = CriarCompeticao(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify(novo.dici()), 201

@Competicao_Blueprint.route('/<int:id>', methods=["PUT"])
def update_competicao(id):
    dados = request.get_json()
    atualizado, erro = AtualizarCompeticao(id, dados)
    if erro:
        return jsonify({"erro": erro}), 404
    return jsonify(atualizado.dici())

@Competicao_Blueprint.route('/<int:id>', methods=["DELETE"])
def delete_competicao(id):
    sucesso, erro = DeletarCompeticao(id)
    if not sucesso:
        return jsonify({"erro": erro}), 404
    return jsonify({"mensagem": "Competição deletada com sucesso"})