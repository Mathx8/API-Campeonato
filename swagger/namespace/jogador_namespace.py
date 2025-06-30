from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.jogador import ListarJogadores, ListarJogadorPorNome, CriarJogador, AtualizarJogador, DeletarJogador

jogador_ns = Namespace("Jogador", description="Operações relacionadas aos jogadores")

jogador_model = jogador_ns.model("Jogador", {
    "nome": fields.String(required=True, description="Nick do Jogador", example = 'RolaTuai'),
    "posicao": fields.String(required=True, description="Posição do Jogador", example = 'ATK')
})

time_model = jogador_ns.model("Time", {
    "id": fields.Integer(description="ID do Time", example=1),
    "nome": fields.String(description="Nome do Time", example="São Paulo"),
    "competicao": fields.String(description="Nome da Competição", example="Libertadores")
})

jogador_output_model = jogador_ns.model("JogadorOutput", {
    "id": fields.Integer(description="ID do Jogador", example=1),
    "nome": fields.String(description="Nome do Jogador", example="RolaTuai"),
    "posicao": fields.String(description="Posição do Jogador", example="ATK"),
    "gols": fields.Integer(description="Quantidade de gols marcados", example=5),
    "assistencias": fields.Integer(description="Quantidade de assistências", example=3),
    "gols_contra": fields.Integer(description="Gols contra", example=1),
    "cartoes_amarelos": fields.Integer(description="Cartões amarelos recebidos", example=2),
    "cartoes_vermelhos": fields.Integer(description="Cartões vermelhos recebidos", example=1),
    "mvps": fields.Integer(description="Quantidade de vezes eleito MVP", example=4),
    "times": fields.List(fields.Nested(time_model), description="Times pelos quais jogou")
})

erro_model = jogador_ns.model("Erro", {
    "mensagem": fields.String(example="Jogador não encontrado")
})

@jogador_ns.route('/view')
class JogadorViewResource(Resource):
    @jogador_ns.marshal_list_with(jogador_output_model)
    def get(self):
        """Lista todos os jogadores"""
        jogadores = ListarJogadores()
        
        if not jogadores:
            return {"message": "Nenhum jogador cadastrado"}, 200
            
        return [j.dici() for j in jogadores], 200

@jogador_ns.route('/')
class JogadorResource(Resource):
    @jogador_ns.expect(jogador_model)
    @jogador_ns.response(201, "Jogador criado com sucesso", model=jogador_output_model)
    @jogador_ns.response(400, "Dados inválidos", model=erro_model)
    @editor_ou_admin
    def post(self):
        """Cria um novo jogador"""
        dados = jogador_ns.payload
        jogador, erro = CriarJogador(dados)
        if erro:
            return {"mensagem": erro}, 400
        return jogador.dici(), 201

@jogador_ns.route('/buscar/<string:nome>')
class JogadorPorNomeResource(Resource):
    @jogador_ns.response(200, "Jogador encontrado", model=jogador_output_model)
    @jogador_ns.response(404, "Jogador não encontrado", model=erro_model)
    def get(self, nome):
        """Obtém um jogador pelo nome"""
        jogador = ListarJogadorPorNome(nome)
        if not jogador:
            return {"mensagem": "Jogador não encontrado"}, 404
        return jogador.dici(), 200

@jogador_ns.route('/<int:id_jogador>')
class JogadorIdResource(Resource):
    @jogador_ns.expect(jogador_model)
    @jogador_ns.marshal_with(jogador_output_model)
    @jogador_ns.response(200, "Jogador atualizado com sucesso", model=jogador_output_model)
    @jogador_ns.response(404, "Jogador não encontrado", model=erro_model)
    @editor_ou_admin
    def put(self, id_jogador):
        """Atualiza um jogador existente"""
        dados = jogador_ns.payload
        jogador, erro = AtualizarJogador(id_jogador, dados)
        if erro:
            return {"mensagem": erro}, 404
        return jogador, 200

    @jogador_ns.response(200, "Jogador excluído com sucesso")
    @jogador_ns.response(404, "Jogador não encontrado", model=erro_model)
    @editor_ou_admin
    def delete(self, id_jogador):
        """Remove um jogador"""
        sucesso, erro = DeletarJogador(id_jogador)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Jogador deletado com sucesso"}, 200