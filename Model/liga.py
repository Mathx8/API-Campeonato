from flask import request
from config import db
from Model.competicao import Competicao

class Liga(Competicao):
    __tablename__ = "liga"

    id = db.Column(db.Integer, db.ForeignKey('competicao.id'), primary_key=True)
    usar_grupos = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'liga'
    }

    grupos = db.relationship("Grupo", back_populates="liga", cascade="all, delete-orphan")
    partidas = db.relationship("Partida", back_populates="competicao", overlaps="competicao")

    def __init__(self, nome, usar_grupos=True):
        super().__init__(nome=nome, tipo='liga')
        self.usar_grupos = usar_grupos

    def __repr__(self):
        return self.nome

    def dici(self, grupo_nome=None):
        response = {
            "id": self.id,
            "nome": self.nome,
            "tipo": "liga",
            "partidas": [p.dici() for p in self.partidas]
        }

        if grupo_nome and self.usar_grupos:
            grupo = next((g for g in self.grupos if g.nome == grupo_nome), None)
            if grupo:
                response["grupo"] = grupo.dici()

        return response