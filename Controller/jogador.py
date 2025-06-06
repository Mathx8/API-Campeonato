from flask import Blueprint, jsonify
from Model.jogador import *

Jogador_Blueprint = Blueprint('jogador', __name__)

@Jogador_Blueprint.route('/', methods=["GET"])
def get_jogadores():
    jogadores = ListarJogadores()
    return jsonify([j.dici() for j in jogadores])

@Jogador_Blueprint.route('/buscar/<string:nome>', methods=["GET"])
def get_jogador_por_nome(nome):
    jogador = ListarJogadorPorNome(nome)
    if not jogador:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    return jsonify(jogador.dici())

@Jogador_Blueprint.route('/', methods=["POST"])
def create_jogador():
    dados = request.get_json()
    novo, erro = CriarJogador(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify(novo.dici()), 201

@Jogador_Blueprint.route('/<int:id>', methods=["PUT"])
def update_jogador(id):
    dados = request.get_json()
    atualizado, erro = AtualizarJogador(id, dados)
    if erro:
        return jsonify({"erro": erro}), 404
    return jsonify(atualizado.dici())

@Jogador_Blueprint.route('/<int:id>', methods=["DELETE"])
def delete_jogador(id):
    sucesso, erro = DeletarJogador(id)
    if not sucesso:
        return jsonify({"erro": erro}), 404
    return jsonify({"mensagem": "Jogador deletado com sucesso"})