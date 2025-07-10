from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.sumula import ( ListarSumulas, BuscarSumulaPorId, CriarSumula, AtualizarSumula, DeletarSumula)

sumula_ns = Namespace("Sumula", description="Operações relacionadas às súmulas das partidas")

jogador_evento_model = sumula_ns.model("JogadorEvento", {
    "jogador_id": fields.Integer(required=True, example=1, description="ID do jogador que marcou o gol ou fez o gol contra"),
    "assistencia_id": fields.Integer(required=False, example=2, description="ID do jogador que deu a assistência (omitido em gol contra)"),
    "contra": fields.Boolean(required=False, default=False, example=False, description="Se o gol foi contra")
})

cartao_model = sumula_ns.model("CartaoEvento", {
    "jogador_id": fields.Integer(required=True, example=4, description="ID do jogador que recebeu o cartão"),
    "tipo": fields.String(required=True, example="amarelo", description="Tipo do cartão: amarelo ou vermelho")
})

sumula_input_model = sumula_ns.model("SumulaInput", {
    "partida_id": fields.Integer(required=True, example=1, description="ID da partida"),
    "mvp_id": fields.Integer(required=True, example=5, description="ID do jogador MVP"),
    "gols": fields.List(fields.Nested(jogador_evento_model), description="Lista de gols na partida"),
    "cleansheets": fields.List(fields.Integer, description="IDs dos jogadores que conseguiram clean sheet"),
    "cartoes": fields.List(fields.Nested(cartao_model), description="Lista de cartões da partida")
})

sumula_output_model = sumula_ns.model("SumulaOutput", {
    "id": fields.Integer,
    "partida_id": fields.Integer,
    "mvp": fields.String,
    "gols": fields.List(fields.Raw),
    "cleansheets": fields.List(fields.Raw),
    "cartoes": fields.List(fields.Raw)
})

erro_model = sumula_ns.model("Erro", {
    "mensagem": fields.String
})

@sumula_ns.route('/')
class SumulaCreateResource(Resource):
    @sumula_ns.expect(sumula_input_model)
    @sumula_ns.marshal_with(sumula_output_model)
    @sumula_ns.response(201, "Súmula criada com sucesso")
    @sumula_ns.response(400, "Erro ao criar súmula", model=erro_model)
    @editor_ou_admin
    def post(self):
        """Cria uma nova súmula"""
        dados = sumula_ns.payload
        sumula, erro = CriarSumula(dados)
        if erro:
            return {"mensagem": erro}, 400
        return sumula.dici(), 201

@sumula_ns.route('/view')
class SumulaViewResource(Resource):
    @sumula_ns.marshal_list_with(sumula_output_model)
    def get(self):
        """Lista todas as súmulas"""
        sumulas = ListarSumulas()
        return [s.dici() for s in sumulas], 200

@sumula_ns.route('/<int:sumula_id>')
class SumulaResource(Resource):
    @sumula_ns.marshal_with(sumula_output_model)
    @sumula_ns.response(404, "Súmula não encontrada", model=erro_model)
    def get(self, sumula_id):
        """Busca uma súmula pelo ID"""
        sumula = BuscarSumulaPorId(sumula_id)
        if not sumula:
            return {"mensagem": "Súmula não encontrada"}, 404
        return sumula.dici(), 200

    @sumula_ns.expect(sumula_input_model)
    @sumula_ns.marshal_with(sumula_output_model)
    @sumula_ns.response(200, "Súmula atualizada com sucesso")
    @sumula_ns.response(404, "Súmula não encontrada", model=erro_model)
    @editor_ou_admin
    def put(self, sumula_id):
        """Atualiza uma súmula existente"""
        dados = sumula_ns.payload
        sumula, erro = AtualizarSumula(sumula_id, dados)
        if erro:
            return {"mensagem": erro}, 404
        return sumula.dici(), 200

    @sumula_ns.response(200, "Súmula deletada com sucesso")
    @sumula_ns.response(404, "Súmula não encontrada", model=erro_model)
    @editor_ou_admin
    def delete(self, sumula_id):
        """Remove uma súmula"""
        sucesso, erro = DeletarSumula(sumula_id)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Súmula deletada com sucesso"}, 200