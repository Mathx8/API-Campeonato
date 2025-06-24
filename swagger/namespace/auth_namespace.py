from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
from Controller.decorators import admin_required, editor_ou_admin
from Model.usuario import ( Usuario, criar_usuario, criar_editor_sem_senha, autenticar_usuario, definir_senha)

api = Namespace("Usuário", description="Autenticação e gerenciamento de usuários")

usuario_model = api.model("Usuario", {
    "username": fields.String(required=True),
    "senha": fields.String(required=True),
    "papel": fields.String(required=True, enum=["admin", "editor"])
})

novo_editor_model = api.model("NovoEditor", {
    "username": fields.String(required=True)
})

login_model = api.model("Login", {
    "username": fields.String(required=True),
    "senha": fields.String(required=True)
})

definir_senha_model = api.model("DefinirSenha", {
    "username": fields.String(required=True),
    "nova_senha": fields.String(required=True)
})

usuario_response_model = api.model("UsuarioResposta", {
    "id": fields.Integer,
    "username": fields.String,
    "papel": fields.String
})

@api.route("/register")
class Register(Resource):
    @api.expect(usuario_model)
    @admin_required
    def post(self):
        """Admin cria usuário com senha"""
        dados = request.get_json()
        novo, erro = criar_usuario(dados['username'], dados['senha'], dados['papel'])
        if erro:
            return {"mensagem": erro}, 400
        return novo.to_dict(), 201

@api.route("/register-editor")
class RegisterEditor(Resource):
    @api.expect(novo_editor_model)
    @admin_required
    def post(self):
        """Admin cria editor sem senha"""
        dados = request.get_json()
        novo, erro = criar_editor_sem_senha(dados["username"])
        if erro:
            return {"mensagem": erro}, 400
        return novo.to_dict(), 201

@api.route("/definir-senha")
class DefinirSenha(Resource):
    @api.expect(definir_senha_model)
    def post(self):
        """Editor define a senha no primeiro login"""
        dados = request.get_json()
        usuario, erro = definir_senha(dados["username"], dados["nova_senha"])
        if erro:
            return {"mensagem": erro}, 400
        return {"mensagem": "Senha definida com sucesso"}, 200

@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Login de usuário"""
        dados = request.get_json()
        usuario = autenticar_usuario(dados['username'], dados['senha'])
        if not usuario:
            return {"mensagem": "Usuário ou senha inválidos"}, 401
        token = create_access_token(identity=str(usuario.id), expires_delta=timedelta(hours=12))
        return {"access_token": token, "papel": usuario.papel}, 200

@api.route("/listar")
class ListarUsuarios(Resource):
    @api.marshal_list_with(usuario_response_model)
    @admin_required
    def get(self):
        """Listar todos os usuários"""
        usuarios = Usuario.query.all()
        return [u.to_dict() for u in usuarios]

@api.route("/me")
class UsuarioAtual(Resource):
    @api.marshal_with(usuario_response_model)
    @editor_ou_admin
    def get(self):
        """Ver dados do usuário logado"""
        user_id = get_jwt_identity()
        usuario = Usuario.query.get(user_id)
        return usuario.to_dict()