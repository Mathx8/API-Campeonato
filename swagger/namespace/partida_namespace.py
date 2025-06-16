from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.partida import ListarPartidas, ListarPartidasPorRodada, ListarPartidaPorId, CriarPartida, AtualizarPartida, DeletarPartida

partida_ns = Namespace("Partida", description="Operações relacionadas às partidas")

partida_model = partida_ns.model("Partida", {
    "competicao_id": fields.Integer(required=False, description="ID da competição (opcional)"),
    "grupo_id": fields.Integer(required=False, description="ID do grupo (caso seja uma liga)"),
    "time_casa_id": fields.Integer(required=True, example=1),
    "time_fora_id": fields.Integer(required=True, example=2),
    "gols_casa": fields.Integer(required=False, example=2),
    "gols_fora": fields.Integer(required=False, example=1),
    "rodada": fields.String(required=True, example=3)
})

partida_view = partida_ns.model("PartidaView", {
    "competicao": fields.String(
        description="Nome da competição (liga ou torneio)",
        example="Campeonato Brasileiro"
    ),
    "competicao_id": fields.Integer(
        description="ID da competição",
        example=1
    ),
    "rodada": fields.String(required=True, example=3),
    "time_casa": fields.String(example="Flamengo"),
    "gols_casa": fields.Integer(example=2),
    "time_fora": fields.String(example="Vasco"),
    "gols_fora": fields.Integer(example=1),
})

partida_model_output = partida_ns.model("PartidaOutput", {
    "id": fields.Integer(example=1),
    "competicao": fields.String(
        description="Nome da competição (liga ou torneio)",
        example="Campeonato Brasileiro"
    ),
    "competicao_id": fields.Integer(
        description="ID da competição",
        example=1
    ),
    "rodada": fields.String(example=1),
    "time_casa": fields.String(example="Flamengo"),
    "time_fora": fields.String(example="Vasco"),
    "gols_casa": fields.Integer(example=2),
    "gols_fora": fields.Integer(example=1),
    "time_casa_id": fields.Integer(example=1),
    "time_fora_id": fields.Integer(example=2)
})


erro_model = partida_ns.model("Erro", {
    "erro": fields.String(example="Partida não encontrada")
})

@partida_ns.route('/')
class PartidaResource(Resource):
    @partida_ns.marshal_list_with(partida_view)
    @cross_origin()
    def get(self):
        """Lista todas as partidas"""
        partidas = ListarPartidas()
        return [p.dici() for p in partidas]

    @partida_ns.expect(partida_model)
    @partida_ns.response(201, "Partida criada com sucesso", partida_model_output)
    @partida_ns.response(400, "Dados inválidos", erro_model)
    @editor_ou_admin
    def post(self):
        """Cria uma nova partida"""
        dados = partida_ns.payload
        partida, erro = CriarPartida(dados)
        if erro:
            return {"erro": erro}, 400
        return partida.dici(), 201
    
@partida_ns.route('/rodada/<string:rodada>')
class PartidaPorRodadaResource(Resource):
    @partida_ns.marshal_list_with(partida_view)
    @partida_ns.response(200, "Lista de partidas da rodada")
    def get(self, rodada):
        """Lista as partidas pela rodada"""
        return ListarPartidasPorRodada(rodada)

@partida_ns.route('/<int:id>')
class PartidaIdResource(Resource):
    @partida_ns.marshal_with(partida_model_output)
    @partida_ns.response(404, "Partida não encontrada", model=erro_model)
    def get(self, id):
        """Obtém uma partida pelo ID"""
        partida = ListarPartidaPorId(id)
        if not partida:
            return {"erro": "Partida não encontrada"}, 404
        return partida.dici()

    @partida_ns.expect(partida_model)
    @partida_ns.response(200, "Partida atualizada", partida_model_output)
    @partida_ns.response(404, "Partida não encontrada", erro_model)
    @editor_ou_admin
    def put(self, id):
        """Atualiza uma partida existente"""
        dados = partida_ns.payload
        partida, erro = AtualizarPartida(id, dados)
        if erro:
            return {"erro": erro}, 404
        return partida.dici()

    @partida_ns.response(204, "Partida deletada com sucesso")
    @partida_ns.response(404, "Partida não encontrada", erro_model)
    @editor_ou_admin
    def delete(self, id):
        """Remove uma partida"""
        sucesso, erro = DeletarPartida(id)
        if not sucesso:
            return {"erro": erro}, 404
        return '', 204
