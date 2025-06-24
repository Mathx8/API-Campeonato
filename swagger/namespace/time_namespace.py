from flask_restx import Namespace, Resource, fields
from Controller.decorators import editor_ou_admin
from Model.time import ListarTimes, ListarTimePorId, CriarTime, AtualizarTime, DeletarTime, AdicionarJogadoresAoTime, RemoverJogadoresDoTime

time_ns = Namespace("Time", description="Operações relacionadas aos times")

time_model = time_ns.model("Time", {
    "nome": fields.String(required=True, description="Nome do time", example="Cruzeiro"),
    "logo": fields.String(required=False, description="URL da logo do time", example="https://exemplo.com/logo.png"),
    "competicao_id": fields.Integer(required=False, description="ID da Competição", example=1),
    "grupo_id": fields.Integer(required=False, description="ID do Grupo (se aplicável)", example=2)
})

time_view = time_ns.model("TimeView", {
    "nome": fields.String(required=True, description="Nome do time", example="Cruzeiro"),
    "competicao": fields.Nested(time_ns.model("CompeticaoInfo", {
        "id": fields.Integer(example=1),
        "nome": fields.String(example="Brasileirão"),
        "tipo": fields.String(example="Liga")
    }), allow_null=True),
    "grupo": fields.Nested(time_ns.model("GrupoInfo", {
        "id": fields.Integer(example=2),
        "nome": fields.String(example="Grupo A")
    }), allow_null=True),
    "jogadores": fields.List(fields.Raw(example={"id": 1, "nome": "RolaTuai", "posicao": "ATK"}))
})

time_model_output = time_ns.clone("TimeOutput", time_model, {
    "id": fields.Integer(description="ID do Time", example=1),
    "nome": fields.String(description="Nome do Time", example="Cruzeiro"),
    "competicao": fields.Nested(time_ns.model("CompeticaoInfo", {
        "id": fields.Integer(example=1),
        "nome": fields.String(example="Brasileirão"),
        "tipo": fields.String(example="Liga")
    }), allow_null=True),
    "grupo": fields.Nested(time_ns.model("GrupoInfo", {
        "id": fields.Integer(example=2),
        "nome": fields.String(example="Grupo A")
    }), allow_null=True),
    "jogadores": fields.List(fields.Raw(example={"id": 1, "nome": "RolaTuai", "posicao": "ATK"}))
})

jogador_ids_model = time_ns.model("JogadorIds", {
    "jogador_ids": fields.List(fields.Integer, required=True, description="Lista de IDs dos jogadores")
})

erro_model = time_ns.model("Erro", {
    "erro": fields.String(example="Time não encontrado")
})

@time_ns.route('/view')
class TimeViewResource(Resource):
    @time_ns.marshal_list_with(time_view)
    def get(self):
        """Lista todos os times"""
        times = ListarTimes()
        
        if not times:
            return {"message": "Nenhum time cadastrado"}, 200
            
        return [t.dici() for t in times], 200

@time_ns.route('/')
class TimeResource(Resource):
    @time_ns.expect(time_model)
    @time_ns.response(201, "Time criado com sucesso", time_model_output)
    @time_ns.response(400, "Dados inválidos", erro_model)
    @editor_ou_admin
    def post(self):
        """Cria um novo time"""
        dados = time_ns.payload
        time, erro = CriarTime(dados)
        if erro:
            time_ns.abort(400, erro)
        return time.dici(), 201

@time_ns.route('/<int:id>')
class TimeIdResource(Resource):
    @time_ns.marshal_with(time_model_output)
    @time_ns.response(404, "Time não encontrado", model=erro_model)
    def get(self, id):
        """Obtém um time pelo ID"""
        time = ListarTimePorId(id)
        if not time:
            time_ns.abort(404, "Time não encontrado")
        return time.dici()

    @time_ns.expect(time_model)
    @time_ns.response(200, "Time atualizado", time_model_output)
    @time_ns.response(404, "Time não encontrado", erro_model)
    @editor_ou_admin
    def put(self, id):
        """Atualiza um time existente"""
        dados = time_ns.payload
        time, erro = AtualizarTime(id, dados)
        if erro:
            status = 404 if "não encontrado" in erro else 400
            time_ns.abort(status, erro)
        return time.dici()

    @time_ns.response(204, "Time deletado com sucesso")
    @time_ns.response(404, "Time não encontrado", erro_model)
    @editor_ou_admin
    def delete(self, id):
        """Remove um time"""
        sucesso, erro = DeletarTime(id)
        if not sucesso:
            time_ns.abort(404, erro)
        return '', 204
    
@time_ns.route('/<int:id>/jogadores')
class TimeJogadoresResource(Resource):
    @time_ns.expect(jogador_ids_model)
    @time_ns.response(200, "Jogadores adicionados com sucesso", time_model_output)
    @time_ns.response(400, "Dados inválidos", erro_model)
    @time_ns.response(404, "Time não encontrado", erro_model)
    @editor_ou_admin
    def post(self, id):
        """Adiciona jogadores a um time"""
        dados = time_ns.payload
        time, erro = AdicionarJogadoresAoTime(id, dados)
        if erro:
            status = 404 if "não encontrado" in erro else 400
            time_ns.abort(status, erro)
        return time.dici(), 200

    @time_ns.expect(jogador_ids_model)
    @time_ns.response(200, "Jogadores removidos com sucesso", time_model_output)
    @time_ns.response(400, "Dados inválidos", erro_model)
    @time_ns.response(404, "Time não encontrado", erro_model)
    @editor_ou_admin
    def delete(self, id):
        """Remove jogadores de um time"""
        dados = time_ns.payload
        time, erro = RemoverJogadoresDoTime(id, dados)
        if erro:
            status = 404 if "não encontrado" in erro else 400
            time_ns.abort(status, erro)
        return time.dici(), 200