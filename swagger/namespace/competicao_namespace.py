from flask_restx import Namespace, Resource, fields
from Model.competicao import ListarCompeticoes, ListarCompeticaoPorId, CriarCompeticao, AtualizarCompeticao, DeletarCompeticao

competicao_ns = Namespace("Competicao", description="Operações relacionadas às competições")

competicao_model = competicao_ns.model("Competicao", {
    "nome": fields.String(required=True, description="Nome da Competição", example='Campeonato Brasileiro'),
    "tipo": fields.String(required=True, description="Tipo da Competição", enum=['liga', 'torneio'], example='liga ou torneio')
})

competicao_output_model = competicao_ns.model("CompeticaoOutput", {
    "id": fields.Integer(description="ID da Competição", example=1),
    "nome": fields.String(description="Nome da Competição", example="Campeonato Brasileiro"),
    "tipo": fields.String(description="Tipo da Competição", example="liga")
})

erro_model = competicao_ns.model("Erro", {
    "mensagem": fields.String(example="Competição não encontrada")
})

@competicao_ns.route('/')
class CompeticaoResource(Resource):
    @competicao_ns.marshal_list_with(competicao_output_model)
    def get(self):
        """Lista todas as competições"""
        return ListarCompeticoes()
    
    @competicao_ns.expect(competicao_model)
    @competicao_ns.response(201, "Competição criada com sucesso", model=competicao_output_model)
    @competicao_ns.response(400, "Dados inválidos", model=erro_model)
    def post(self):
        """Cria uma nova competição"""
        dados = competicao_ns.payload
        competicao, erro = CriarCompeticao(dados)
        if erro:
            return {"mensagem": erro}, 400
        return competicao.to_dict(), 201

@competicao_ns.route('/<int:id_competicao>')
class CompeticaoIdResource(Resource):
    @competicao_ns.response(200, "Competição encontrada", model=competicao_output_model)
    @competicao_ns.response(404, "Competição não encontrada", model=erro_model)
    def get(self, id_competicao):
        """Obtém uma competição pelo ID"""
        competicao = ListarCompeticaoPorId(id_competicao)
        if not competicao:
            return {"mensagem": "Competição não encontrada"}, 404
        return competicao.to_dict(), 200

    @competicao_ns.expect(competicao_model)
    @competicao_ns.response(200, "Competição atualizada com sucesso", model=competicao_output_model)
    @competicao_ns.response(404, "Competição não encontrada", model=erro_model)
    def put(self, id_competicao):
        """Atualiza uma competição existente"""
        dados = competicao_ns.payload
        competicao, erro = AtualizarCompeticao(id_competicao, dados)
        if erro:
            return {"mensagem": erro}, 404
        return competicao.to_dict(), 200

    @competicao_ns.response(200, "Competição excluída com sucesso")
    @competicao_ns.response(404, "Competição não encontrada", model=erro_model)
    def delete(self, id_competicao):
        """Remove uma competição"""
        sucesso, erro = DeletarCompeticao(id_competicao)
        if not sucesso:
            return {"mensagem": erro}, 404
        return {"mensagem": "Competição deletada com sucesso"}, 200