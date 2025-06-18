from flask_restx import Namespace, Resource, fields
from flask import request
from Controller.decorators import admin_required, editor_ou_admin
from Model.usuario import Usuario, criar_usuario, autenticar_usuario
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta

api = Namespace("Usuário", description="Autenticação e gerenciamento de usuários")

usuario_model = api.model("Usuario", {
    "username": fields.String(required=True),
    "senha": fields.String(required=True),
    "papel": fields.String(required=True, enum=["admin", "editor"])
})

login_model = api.model("Login", {
    "username": fields.String(required=True),
    "senha": fields.String(required=True)
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
        """Registro"""
        dados = request.get_json()
        novo, erro = criar_usuario(dados['username'], dados['senha'], dados['papel'])
        if erro:
            return {"mensagem": erro}, 400
        return novo.to_dict(), 201

@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Login"""
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
        """Listar todos os usuários (admin apenas)"""
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