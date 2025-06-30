from flask import request
from Model.jogador_time import jogador_time
from Model.time import Time
from config import db

class Jogador(db.Model):
    __tablename__ = "jogador"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    posicao = db.Column(db.String(3), nullable=False)

    times = db.relationship("Time", secondary=jogador_time, back_populates="jogadores")

    def __init__(self, nome, posicao):
        self.nome = nome
        self.posicao = posicao

    def contar_estatisticas(self):
        from Model.sumula import Gol, Cartao, Sumula

        gols = Gol.query.filter_by(jogador_id=self.id, contra=False).count()
        assistencias = Gol.query.filter(Gol.assistencia_id == self.id).count()
        gols_contra = Gol.query.filter_by(jogador_id=self.id, contra=True).count()
        amarelos = Cartao.query.filter_by(jogador_id=self.id, tipo='amarelo').count()
        vermelhos = Cartao.query.filter_by(jogador_id=self.id, tipo='vermelho').count()
        mvps = Sumula.query.filter_by(mvp_id=self.id).count()

        return {
            "gols": gols,
            "assistencias": assistencias,
            "gols_contra": gols_contra,
            "cartoes_amarelos": amarelos,
            "cartoes_vermelhos": vermelhos,
            "mvps": mvps
        }

    def dici(self):
        estatisticas = self.contar_estatisticas()
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao": self.posicao,
            **estatisticas,
            "times": [{"id": t.id, "nome": t.nome, "competicao": t.competicao} for t in self.times]
        }

def ListarJogadores():
    return Jogador.query.all()

def ListarJogadorPorNome(NomeJogador):
    return Jogador.query.filter_by(nome=NomeJogador).first()

def CriarJogador(dados):
    nome = dados.get("nome")
    posicao = dados.get("posicao")
    times_ids = dados.get("times_ids", [])
    if not nome:
        return None, "Nome é obrigatório"
    if not posicao:
        return None, "Posição é obrigatória"

    novoJogador = Jogador(nome=nome, posicao=posicao)

    for time_id in times_ids:
        time = Time.query.get(time_id)
        if time:
            novoJogador.times.append(time)

    db.session.add(novoJogador)
    db.session.commit()

    return novoJogador, None

def AtualizarJogador(idJogador, dados):
    jogador = Jogador.query.get(idJogador)
    if not jogador:
        return None, "Jogador não encontrado"

    jogador.nome = dados.get("nome", jogador.nome)
    jogador.posicao = dados.get("posicao", jogador.posicao)

    if "times_ids" in dados:
        jogador.times = []
        for time_id in dados["times_ids"]:
            time = Time.query.get(time_id)
            if time:
                jogador.times.append(time)

    db.session.commit()
    return jogador, None

def DeletarJogador(idJogador):
    jogador = Jogador.query.get(idJogador)
    if not jogador:
        return False, "Jogador não encontrado"

    db.session.delete(jogador)
    db.session.commit()
    return True, None