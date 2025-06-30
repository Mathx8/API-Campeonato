from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.premiacao import ( ListarPremiacoes, BuscarPremiacaoPorId, CriarPremiacao, AtualizarPremiacao, DeletarPremiacao)

premiacao_ns = Namespace("Premiacao", description="Operações relacionadas à premiação dos jogadores")

premiacao_input_model = premiacao_ns.model("PremiacaoInput", {
    "competicao_id": fields.Integer(required=True, example=1),
    "mvp_id": fields.Integer(required=False, example=10),
    "artilheiro_id": fields.Integer(required=False, example=11),
    "luva_de_ouro_id": fields.Integer(required=False, example=12),
    "revelacao_id": fields.Integer(required=False, example=13),
    "top_gk_ids": fields.List(fields.Integer, description="IDs dos TOP 3 GKs"),
    "top_zag_ids": fields.List(fields.Integer, description="IDs dos TOP 3 ZAGs"),
    "top_mid_ids": fields.List(fields.Integer, description="IDs dos TOP 3 MIDs"),
    "top_atk_ids": fields.List(fields.Integer, description="IDs dos TOP 3 ATKs"),
    "campeao_id": fields.Integer(required=False, description="ID do time campeão", example=5)
})

premiacao_output_model = premiacao_ns.model("PremiacaoOutput", {
    "id": fields.Integer,
    "competicao": fields.Integer,
    "mvp": fields.String,
    "artilheiro": fields.String,
    "luva_de_ouro": fields.String,
    "revelacao": fields.String,
    "top_gk": fields.List(fields.String),
    "top_zag": fields.List(fields.String),
    "top_mid": fields.List(fields.String),
    "top_atk": fields.List(fields.String),
    "campeao": fields.String(description="Nome do time campeão")
})

erro_model = premiacao_ns.model("Erro", {
    "mensagem": fields.String
})

@premiacao_ns.route('/view')
class PremiacaoViewResource(Resource):
    @premiacao_ns.marshal_list_with(premiacao_output_model)
    def get(self):
        """Lista todas as premiações"""
        premiacoes = ListarPremiacoes()
        return [p.dici() for p in premiacoes], 200


@premiacao_ns.route('/<int:premiacao_id>')
class PremiacaoResource(Resource):
    @premiacao_ns.marshal_with(premiacao_output_model)
    @premiacao_ns.response(404, "Premiação não encontrada", model=erro_model)
    def get(self, premiacao_id):
        """Busca uma premiação pelo ID"""
        premiacao = BuscarPremiacaoPorId(premiacao_id)
        if not premiacao:
            return {"mensagem": "Premiação não encontrada"}, 404
        return premiacao.dici(), 200

    @premiacao_ns.expect(premiacao_input_model)
    @premiacao_ns.marshal_with(premiacao_output_model)
    @premiacao_ns.response(200, "Premiação atualizada com sucesso")
    @premiacao_ns.response(404, "Premiação não encontrada", model=erro_model)
    @editor_ou_admin
    def put(self, premiacao_id):
        """Atualiza uma premiação existente"""
        dados = premiacao_ns.payload
        premiacao, erro = AtualizarPremiacao(premiacao_id, dados)
        if erro:
            return {"mensagem": erro}, 404
        return premiacao.dici(), 200

    @premiacao_ns.response(200, "Premiação deletada com sucesso")
    @premiacao_ns.response(404, "Premiação não encontrada", model=erro_model)
    @editor_ou_admin
    def delete(self, premiacao_id):
        """Remove uma premiação"""
        sucesso, erro = DeletarPremiacao(premiacao_id)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Premiação deletada com sucesso"}, 200


@premiacao_ns.route('/')
class PremiacaoCreateResource(Resource):
    @premiacao_ns.expect(premiacao_input_model)
    @premiacao_ns.marshal_with(premiacao_output_model)
    @premiacao_ns.response(201, "Premiação criada com sucesso")
    @premiacao_ns.response(400, "Erro ao criar premiação", model=erro_model)
    @editor_ou_admin
    def post(self):
        """Cria uma nova premiação"""
        dados = premiacao_ns.payload
        premiacao, erro = CriarPremiacao(dados)
        if erro:
            return {"mensagem": erro}, 400
        return premiacao.dici(), 201