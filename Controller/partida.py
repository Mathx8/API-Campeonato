from flask import Blueprint, jsonify
from Model.partida import *

Partida_Blueprint = Blueprint("partida", __name__)

@Partida_Blueprint.route("/", methods=["GET"])
def listar_partidas():
    partidas = ListarPartidas()
    return jsonify([p.dici() for p in partidas])

@Partida_Blueprint.route("/rodada/<int:rodada>", methods=["GET"])
def get_partidas_por_rodada(rodada):
    rodada = ListarPartidasPorRodada(rodada)
    if not rodada:
        return jsonify({"erro": "Rodada não encontrada"}), 404
    return jsonify(rodada.dici())

@Partida_Blueprint.route("/<int:id>", methods=["GET"])
def get_partida_por_id(id):
    partida = ListarPartidaPorId(id)
    if not partida:
        return jsonify({"erro": "Partida não encontrada"}), 404
    return jsonify(partida.dici())

@Partida_Blueprint.route("/", methods=["POST"])
def create_partida():
    dados = request.get_json()
    nova, erro = CriarPartida(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify(nova.dici()), 201

@Partida_Blueprint.route("/<int:id>", methods=["PUT"])
def update_partida(id):
    dados = request.get_json()
    atualizada, erro = AtualizarPartida(id, dados)
    if erro:
        return jsonify({"erro": erro}), 404
    return jsonify(atualizada.dici())

@Partida_Blueprint.route("/<int:id>", methods=["DELETE"])
def delete_partida(id):
    sucesso, erro = DeletarPartida(id)
    if not sucesso:
        return jsonify({"erro": erro}), 404
    return jsonify({"mensagem": "Partida deletada com sucesso"})
