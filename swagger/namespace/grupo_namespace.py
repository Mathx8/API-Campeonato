from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.grupo import (ListarGrupos, ListarGrupoPorId, CriarGrupo, AtualizarGrupo, DeletarGrupo, ObterClassificacaoPorGrupoId)

grupo_ns = Namespace("Grupo", description="Operações relacionadas aos grupos de competições")

time_classificacao_model = grupo_ns.model("TimeClassificacao", {
    "id": fields.Integer(description="ID do time"),
    "nome": fields.String(description="Nome do time"),
    "pontos": fields.Integer(description="Pontuação do time"),
    "vitorias": fields.Integer(description="Número de vitórias"),
    "empates": fields.Integer(description="Número de empates"),
    "derrotas": fields.Integer(description="Número de derrotas"),
    "gols_marcados": fields.Integer(description="Gols marcados"),
    "gols_sofridos": fields.Integer(description="Gols sofridos"),
    "saldo_de_gols": fields.Integer(description="Saldo de gols"),
    "jogos" : fields.Integer (description="Número de jogos")
})

time_model = grupo_ns.model("TimeGrupo", {
    "id": fields.Integer(description="ID do time"),
    "nome": fields.String(description="Nome do time"),
})

grupo_model = grupo_ns.model("GrupoInput", {
    "nome": fields.String(required=True, description="Nome do grupo (1-2 caracteres)", example="A"),
    "liga_id": fields.Integer(required=True, description="ID da liga associada", example=1)
})

grupo_output_model = grupo_ns.model("GrupoOutput", {
    "id": fields.Integer(description="ID do grupo"),
    "nome": fields.String(description="Nome do grupo"),
    "liga_id": fields.Integer(description="ID da liga associada"),
    "times": fields.List(fields.Nested(time_model), description="Times do grupo"),
    "classificacao": fields.List(fields.Nested(time_classificacao_model), description="Classificação do grupo")
})

erro_model = grupo_ns.model("Erro", {
    "mensagem": fields.String(example="Grupo não encontrado")
})

@grupo_ns.route('/')
class GrupoResource(Resource):
    @grupo_ns.marshal_list_with(grupo_output_model)
    def get(self):
        """Lista todos os grupos"""
        return ListarGrupos()
    
    @grupo_ns.expect(grupo_model)
    @grupo_ns.response(201, "Grupo criado com sucesso", grupo_output_model)
    @grupo_ns.response(400, "Dados inválidos", erro_model)
    @editor_ou_admin
    def post(self):
        """Cria um novo grupo"""
        dados = grupo_ns.payload
        grupo, erro = CriarGrupo(dados)
        if erro:
            return {"mensagem": erro}, 400
        return grupo.dici(), 201

@grupo_ns.route('/<int:id_grupo>')
class GrupoIdResource(Resource):
    @grupo_ns.response(200, "Grupo encontrado", grupo_output_model)
    @grupo_ns.response(404, "Grupo não encontrado", erro_model)
    def get(self, id_grupo):
        """Obtém um grupo pelo ID"""
        grupo = ListarGrupoPorId(id_grupo)
        if not grupo:
            return {"mensagem": "Grupo não encontrado"}, 404
        return grupo.dici(), 200

    @grupo_ns.expect(grupo_model)
    @grupo_ns.response(200, "Grupo atualizado com sucesso", grupo_output_model)
    @grupo_ns.response(404, "Grupo não encontrado", erro_model)
    @editor_ou_admin
    def put(self, id_grupo):
        """Atualiza um grupo existente"""
        dados = grupo_ns.payload
        grupo, erro = AtualizarGrupo(id_grupo, dados)
        if erro:
            return {"mensagem": erro}, 404
        return grupo.dici(), 200

    @grupo_ns.response(200, "Grupo excluído com sucesso")
    @grupo_ns.response(404, "Grupo não encontrado", erro_model)
    @editor_ou_admin
    def delete(self, id_grupo):
        """Remove um grupo"""
        sucesso, erro = DeletarGrupo(id_grupo)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Grupo deletado com sucesso"}, 200
    
@grupo_ns.route('/<int:id_grupo>/classificacao')
class GrupoClassificacaoResource(Resource):
    def get(self, id_grupo):
        """Obtém a classificação atual do grupo"""
        classificacao, erro = ObterClassificacaoPorGrupoId(id_grupo)
        if erro:
            return {"mensagem": erro}, 404
        return classificacao, 200