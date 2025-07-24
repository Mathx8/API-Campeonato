from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.selecao import (
    ListarSelecoes, BuscarSelecaoPorId, CriarSelecao, AtualizarSelecao, DeletarSelecao
)

selecao_ns = Namespace("Seleção da Rodada", description="Operações relacionadas à seleção da rodada")

time_model = selecao_ns.model("TimeComCompeticao", {
    "id": fields.Integer(example=1),
    "nome": fields.String(example="São Paulo"),
})

jogador_selecao_input = selecao_ns.model("JogadorSelecaoInput", {
    "id": fields.Integer(example=12),
    "nome": fields.String(example="Lucas Silva"),
    "categoria": fields.String(example="MID"),
    "nacionalidade": fields.String(example="Brasileiro"),
    "time": fields.Nested(time_model, allow_null=True)
})

selecao_input_model = selecao_ns.model("SelecaoRodadaInput", {
    "rodada": fields.String(required=True, example="C3"),
    "competicao_id": fields.Integer(required=True, example=5),
    "observacoes": fields.String(required=False, example="Rodada muito ofensiva"),
    "gk": fields.List(fields.Integer, required=False, example=[3, 7]),
    "zag": fields.List(fields.Integer, required=False, example=[5, 8]),
    "mid": fields.List(fields.Integer, required=False, example=[9, 10]),
    "atk": fields.List(fields.Integer, required=False, example=[11, 12])
})

selecao_output_model = selecao_ns.model("SelecaoRodadaOutput", {
    "id": fields.Integer(example=1),
    "rodada": fields.String(example="Rodada 3"),
    "competicao_id": fields.Integer(example=2),
    "competicao": fields.String(example="Brasileirão Série A"),
    "observacoes": fields.String(example="Jogos muito disputados."),
    "jogadores": fields.List(fields.Nested(jogador_selecao_input))
})

erro_model = selecao_ns.model("Erro", {
    "mensagem": fields.String
})

@selecao_ns.route("/")
class SelecaoListResource(Resource):
    @selecao_ns.marshal_list_with(selecao_output_model)
    def get(self):
        """Lista todas as seleções da rodada"""
        selecoes = ListarSelecoes()
        return [s.dici() for s in selecoes], 200

    @selecao_ns.expect(selecao_input_model)
    @selecao_ns.marshal_with(selecao_output_model)
    @selecao_ns.response(201, "Seleção criada com sucesso")
    @selecao_ns.response(400, "Erro ao criar seleção", model=erro_model)
    @editor_ou_admin
    def post(self):
        """Cria uma nova seleção da rodada"""
        dados = selecao_ns.payload
        selecao, erro = CriarSelecao(dados)
        if erro:
            return {"mensagem": erro}, 400
        return selecao.dici(), 201


@selecao_ns.route("/<int:selecao_id>")
class SelecaoResource(Resource):
    @selecao_ns.marshal_with(selecao_output_model)
    @selecao_ns.response(404, "Seleção não encontrada", model=erro_model)
    def get(self, selecao_id):
        """Busca uma seleção da rodada pelo ID"""
        selecao = BuscarSelecaoPorId(selecao_id)
        if not selecao:
            return {"mensagem": "Seleção não encontrada"}, 404
        return selecao.dici(), 200

    @selecao_ns.expect(selecao_input_model)
    @selecao_ns.marshal_with(selecao_output_model)
    @selecao_ns.response(400, "Erro ao atualizar seleção", model=erro_model)
    @selecao_ns.response(404, "Seleção não encontrada", model=erro_model)
    @editor_ou_admin
    def put(self, selecao_id):
        """Atualiza uma seleção da rodada"""
        dados = selecao_ns.payload
        selecao, erro = AtualizarSelecao(selecao_id, dados)
        if erro:
            return {"mensagem": erro}, 400
        return selecao.dici(), 200

    @selecao_ns.response(200, "Seleção deletada com sucesso")
    @selecao_ns.response(404, "Seleção não encontrada", model=erro_model)
    @editor_ou_admin
    def delete(self, selecao_id):
        """Deleta uma seleção da rodada"""
        sucesso, erro = DeletarSelecao(selecao_id)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Seleção deletada com sucesso"}, 200
