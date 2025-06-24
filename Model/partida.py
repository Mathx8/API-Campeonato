from flask import request
from config import db

class Partida(db.Model):
    __tablename__ = "partida"

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)
    competicao_id = db.Column(db.Integer, db.ForeignKey('competicao.id'), nullable=True)
    rodada = db.Column(db.String(20), nullable=False)

    time_casa_id = db.Column(db.Integer, db.ForeignKey("time.id"), nullable=False)
    time_fora_id = db.Column(db.Integer, db.ForeignKey("time.id"), nullable=False)
    gols_casa = db.Column(db.Integer, nullable=True)
    gols_fora = db.Column(db.Integer, nullable=True)

    time_casa = db.relationship("Time", foreign_keys=[time_casa_id])
    time_fora = db.relationship("Time", foreign_keys=[time_fora_id])
    competicao = db.relationship("Competicao", overlaps="liga,torneio")
    liga = db.relationship("Liga", overlaps="competicao")
    torneio = db.relationship("Torneio", overlaps="competicao")
    grupo = db.relationship("Grupo", back_populates="partidas")

    def __init__(self, competicao_id, rodada, time_casa_id, time_fora_id, gols_casa=None, gols_fora=None, grupo_id=None):
        self.competicao_id = competicao_id
        self.rodada = rodada
        self.time_casa_id = time_casa_id
        self.time_fora_id = time_fora_id
        self.gols_casa = gols_casa
        self.gols_fora = gols_fora
        self.grupo_id = grupo_id

    def dici(self):
        return {
            "id": self.id,
            "competicao": self.competicao.nome if self.competicao else None,
            "competicao_id": self.competicao_id,
            "grupo_id": self.grupo_id,
            "rodada": self.rodada,
            "time_casa": self.time_casa.nome if self.time_casa else None,
            "time_casa_id": self.time_casa_id,
            "gols_casa": self.gols_casa,
            "time_fora": self.time_fora.nome if self.time_fora else None,
            "time_fora_id": self.time_fora_id,
            "gols_fora": self.gols_fora
        }

def ListarPartidas():
    return Partida.query.all()

def ListarPartidasPorRodada(rodada):
    return Partida.query.filter(db.func.lower(Partida.rodada) == rodada.lower()).all()

def ListarPartidaPorId(idPartida):
    return Partida.query.get(idPartida)

def CriarPartida(dados):
    required_fields = ["rodada", "time_casa_id", "time_fora_id"]
    if not all(field in dados for field in required_fields):
        return None, "Campos obrigatórios faltando"
    
    from Model.competicao import Competicao
    competicao_id = dados.get("competicao_id")
    if competicao_id and not Competicao.query.get(competicao_id):
        return None, "Competição não encontrada"
    
    from Model.grupo import Grupo
    grupo_id = dados.get("grupo_id")
    if grupo_id:
        grupo = Grupo.query.get(grupo_id)
        if not grupo:
            return None, "Grupo não encontrado"

    from Model.time import Time
    if not Time.query.get(dados["time_casa_id"]):
        return None, "Time da casa não encontrado"
    if not Time.query.get(dados["time_fora_id"]):
        return None, "Time visitante não encontrado"

    novaPartida = Partida(
        competicao_id=competicao_id,
        grupo_id=grupo_id,
        rodada=dados["rodada"],
        time_casa_id=dados["time_casa_id"],
        time_fora_id=dados["time_fora_id"],
        gols_casa=dados.get("gols_casa"),
        gols_fora=dados.get("gols_fora")
    )
    
    db.session.add(novaPartida)
    db.session.commit()
    return novaPartida, None

def AtualizarPartida(idPartida, dados):
    partida = db.session.get(Partida, idPartida)
    if not partida:
        return None, "Partida não encontrada."
    
    from Model.time import Time
    if "time_casa_id" in dados:
        if not db.session.get(Time, dados["time_casa_id"]):
            return None, "Time da casa não encontrado."
        partida.time_casa_id = dados["time_casa_id"]

    if "time_fora_id" in dados:
        if not db.session.get(Time, dados["time_fora_id"]):
            return None, "Time visitante não encontrado."
        partida.time_fora_id = dados["time_fora_id"]

    if partida.time_casa_id == partida.time_fora_id:
        return None, "O time da casa e o time visitante não podem ser o mesmo."

    if "gols_casa" in dados:
        partida.gols_casa = dados["gols_casa"]

    if "gols_fora" in dados:
        partida.gols_fora = dados["gols_fora"]

    if "rodada" in dados:
        partida.rodada = dados["rodada"]

    if "competicao_id" in dados:
        from Model.competicao import Competicao
        if not db.session.get(Competicao, dados["competicao_id"]):
            return None, "Competição não encontrada."
        partida.competicao_id = dados["competicao_id"]

    if "grupo_id" in dados:
        from Model.grupo import Grupo
        if dados["grupo_id"] is not None and not db.session.get(Grupo, dados["grupo_id"]):
            return None, "Grupo não encontrado."
        partida.grupo_id = dados["grupo_id"]

    db.session.commit()
    return partida, None

def DeletarPartida(id):
    partida = Partida.query.get(id)
    if not partida:
        return False, "Partida não encontrada"
    db.session.delete(partida)
    db.session.commit()
    return True, None