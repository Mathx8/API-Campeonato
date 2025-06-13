from config import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.Text, nullable=False)
    papel = db.Column(db.String(20), nullable=False)  # 'admin' ou 'editor'

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "papel": self.papel
        }

def criar_usuario(username, senha, papel):
    if Usuario.query.filter_by(username=username).first():
        return None, "Usuário já existe"
    novo = Usuario(
        username=username,
        senha_hash=generate_password_hash(senha),
        papel=papel
    )
    db.session.add(novo)
    db.session.commit()
    return novo, None

def autenticar_usuario(username, senha):
    user = Usuario.query.filter_by(username=username).first()
    if user and user.verificar_senha(senha):
        return user
    return None
