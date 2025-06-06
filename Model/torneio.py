from flask import request
from config import db
from Model.competicao import Competicao

class Torneio(Competicao):
    __tablename__ = "torneio"

    id = db.Column(db.Integer, db.ForeignKey('competicao.id'), primary_key=True)
    fase_atual = db.Column(db.String(20), default='grupos')
    
    __mapper_args__ = {
        'polymorphic_identity': 'torneio'
    }
    
    partidas = db.relationship("Partida", back_populates="competicao", overlaps="competicao")

    def __init__(self, nome, fase_atual='inscricoes'):
        super().__init__(nome=nome, tipo='torneio')
        self.fase_atual = fase_atual

    def __repr__(self):
        return self.nome
    
    def dici(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": "torneio",
            "fase_atual": self.fase_atual,
            "times": [time.nome for time in self.times],
            "partidas": [p.dici() for p in sorted(self.partidas, key=lambda p: p.rodada)]
        }