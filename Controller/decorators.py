from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from Model.usuario import Usuario
from flask import jsonify

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(int(current_user_id))
        if not user or user.papel != "admin":
            return jsonify({"mensagem": "Acesso restrito a administradores"}), 403
        return func(*args, **kwargs)
    return wrapper

def editor_ou_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(int(current_user_id))
        if not user or user.papel not in ["admin", "editor"]:
            return jsonify({"mensagem": "Acesso negado"}), 403
        return func(*args, **kwargs)
    return wrapper