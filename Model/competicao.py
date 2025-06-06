from flask import request
from config import db

class Competicao(db.Model):
    __tablename__ = "competicao"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'competicao'
    }

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo
        }
    
from Model.liga import Liga
from Model.torneio import Torneio
    
def CriarCompeticao(dados):
    if not dados.get('nome'):
        return None, "Nome da competição é obrigatório"
    
    if dados.get('tipo') not in ['liga', 'torneio']:
        return None, "Tipo deve ser 'liga' ou 'torneio'"
    
    if dados['tipo'] == 'liga':
        competicao = Liga(nome=dados['nome'])
    else:
        competicao = Torneio(nome=dados['nome'])
    
    db.session.add(competicao)
    db.session.commit()
    return competicao, None

def ListarCompeticoes():
    return Competicao.query.all()

def ListarCompeticaoPorId(id):
    return Competicao.query.get(id)

def AtualizarCompeticao(id, dados):
    competicao = Competicao.query.get(id)
    if not competicao:
        return None, "Competição não encontrada"
    
    if 'nome' in dados:
        competicao.nome = dados['nome']
    
    db.session.commit()
    return competicao, None

def DeletarCompeticao(id):
    competicao = Competicao.query.get(id)
    if not competicao:
        return False, "Competição não encontrada"
    
    db.session.delete(competicao)
    db.session.commit()
    return True, None