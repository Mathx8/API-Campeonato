from flask import request
from Model.jogador_time import jogador_time
from Model.competicao import Competicao
from Model.grupo import Grupo
from Model.liga import Liga
from config import db

class Time (db.Model):
    __tablename__ = "time"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    competicao_id = db.Column(db.Integer, db.ForeignKey('competicao.id'), nullable=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

    competicao = db.relationship("Competicao", backref="times")
    grupo = db.relationship("Grupo", back_populates="times")
    jogadores = db.relationship("Jogador", secondary=jogador_time, back_populates="times")

    def __init__(self, nome, logo=None, competicao=None, grupo=None):
        self.nome = nome
        self.logo = logo
        
        if competicao:
            self.competicao = competicao
        if grupo:
            self.grupo = grupo

    def __repr__(self):
        return self.nome

    def dici(self):
        competicao_info = None
        if self.competicao:
            competicao_info = {
                "id": self.competicao.id,
                "nome": self.competicao.nome,
                "tipo": self.competicao.tipo
            }
        
        grupo_info = None
        if self.grupo:
            grupo_info = {
                "id": self.grupo.id,
                "nome": self.grupo.nome
            }
        
        return {
            "id": self.id,
            "nome": self.nome,
            "logo": self.logo,
            "competicao": competicao_info,
            "grupo": grupo_info,
            "jogadores": [j.nome for j in self.jogadores]
        }
    
def ListarTimes():
    return Time.query.all()

def ListarTimePorId(idTime):
    return Time.query.get(idTime)

def CriarTime(dados):
    nome = dados.get("nome")
    logo = dados.get("logo")
    if not nome:
        return None, "Nome é obrigatório"
    if Time.query.filter_by(nome=nome).first():
        return None, "Já existe um time com esse nome"
    
    competicao_id = dados.get("competicao_id")
    grupo_id = dados.get("grupo_id")

    novoTime = Time(nome=nome, logo=logo)

    if competicao_id:
        competicao = Competicao.query.get(competicao_id)
        if not competicao:
            return None, "Competição não encontrada"
        novoTime.competicao = competicao
        
        if grupo_id and isinstance(competicao, Liga) and competicao.usar_grupos:
            grupo = Grupo.query.filter_by(id=grupo_id, liga_id=competicao.id).first()
            if not grupo:
                return None, "Grupo não encontrado ou não pertence à liga"
            novoTime.grupo = grupo

    db.session.add(novoTime)
    db.session.commit()
    return novoTime, None

def AtualizarTime(idTime, dados):
    time = Time.query.get(idTime)
    if not time:
        return None, "Time não encontrado"

    if 'nome' in dados:
        nome = dados['nome']
        if nome and nome != time.nome:
            if Time.query.filter_by(nome=nome).first():
                return None, "Já existe outro time com esse nome"
            time.nome = nome

    if 'logo' in dados:
        time.logo = dados['logo']

    if 'competicao_id' in dados:
        competicao = Competicao.query.get(dados['competicao_id'])
        if not competicao:
            return None, "Competição não encontrada"
        
        time.competicao = competicao
        time.grupo = None

    if 'grupo_id' in dados and time.competicao and isinstance(time.competicao, Liga) and time.competicao.usar_grupos:
        grupo = Grupo.query.filter_by(id=dados['grupo_id'], liga_id=time.competicao.id).first()
        if not grupo:
            return None, "Grupo não encontrado ou não pertence à liga"
        time.grupo = grupo
    
    db.session.commit()
    return time, None

def DeletarTime(idTime):
    time = Time.query.get(idTime)
    if not time:
        return False, "Time não encontrado"

    db.session.delete(time)
    db.session.commit()
    return True, None

def AdicionarJogadoresAoTime(id_time, dados):
    from Model.jogador import Jogador
    time = Time.query.get(id_time)
    if not time:
        return None, "Time não encontrado"

    jogador_ids = dados.get("jogador_ids", [])
    if not jogador_ids:
        return None, "Lista de jogadores vazia"

    for jogador_id in jogador_ids:
        jogador = Jogador.query.get(jogador_id)
        if jogador and jogador not in time.jogadores:
            time.jogadores.append(jogador)

    db.session.commit()
    return time, None

def RemoverJogadoresDoTime(id_time, dados):
    from Model.jogador import Jogador
    time = Time.query.get(id_time)
    if not time:
        return None, "Time não encontrado"

    jogador_ids = dados.get("jogador_ids", [])
    if not jogador_ids:
        return None, "Lista de jogadores vazia"

    for jogador_id in jogador_ids:
        jogador = Jogador.query.get(jogador_id)
        if jogador and jogador in time.jogadores:
            time.jogadores.remove(jogador)

    db.session.commit()
    return time, None