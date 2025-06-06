from flask import Blueprint, jsonify
from Model.time import *

Time_Blueprint = Blueprint('time', __name__)

@Time_Blueprint.route('/', methods=["GET"])
def get_times():
    times = ListarTimes()
    return jsonify([t.dici() for t in times])

@Time_Blueprint.route('/<int:id>', methods=["GET"])
def get_time_por_id(id):
    time = ListarTimePorId(id)
    if not time:
        return jsonify({"erro": "Time não encontrado"}), 404
    return jsonify(time.dici())

@Time_Blueprint.route('/', methods=["POST"])
def create_time():
    dados = request.get_json()
    novo, erro = CriarTime(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify(novo.dici()), 201

@Time_Blueprint.route('/<int:id>', methods=["PUT"])
def update_time(id):
    dados = request.get_json()
    atualizado, erro = AtualizarTime(id, dados)
    if erro:
        return jsonify({"erro": erro}), 404
    return jsonify(atualizado.dici())

@Time_Blueprint.route('/<int:id>', methods=["DELETE"])
def delete_time(id):
    sucesso, erro = DeletarTime(id)
    if not sucesso:
        return jsonify({"erro": erro}), 404
    return jsonify({"mensagem": "Time deletado com sucesso"})
