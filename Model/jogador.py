from flask import request
from Model.jogador_time import jogador_time
from Model.time import Time
from config import db

class Jogador(db.Model):
    __tablename__ = "jogador"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    posicao = db.Column(db.String(3), nullable=False)
    nacionalidade = db.Column(db.String(30), nullable=True)

    times = db.relationship("Time", secondary=jogador_time, back_populates="jogadores")

    def __init__(self, nome, posicao, nacionalidade=None):
        self.nome = nome
        self.posicao = posicao
        self.nacionalidade = nacionalidade

    def contar_estatisticas(self):
        from Model.sumula import Gol, Cartao, Sumula, CleanSheet

        gols = Gol.query.filter_by(jogador_id=self.id, contra=False).count()
        assistencias = Gol.query.filter(Gol.assistencia_id == self.id).count()
        cleansheets = CleanSheet.query.filter_by(jogador_id=self.id).count()
        gols_contra = Gol.query.filter_by(jogador_id=self.id, contra=True).count()
        amarelos = Cartao.query.filter_by(jogador_id=self.id, tipo='amarelo').count()
        vermelhos = Cartao.query.filter_by(jogador_id=self.id, tipo='vermelho').count()
        mvps = Sumula.query.filter_by(mvp_id=self.id).count()

        return {
            "gols": gols,
            "assistencias": assistencias,
            "cleansheets": cleansheets,
            "gols_contra": gols_contra,
            "cartoes_amarelos": amarelos,
            "cartoes_vermelhos": vermelhos,
            "mvps": mvps
        }
    
    def contar_estatisticas_na_competicao(self, competicao_id):
        from Model.sumula import Gol, Cartao, Sumula, CleanSheet
        from Model.partida import Partida

        partidas_ids = db.session.query(Partida.id).filter_by(competicao_id=competicao_id).subquery()

        gols = Gol.query.join(Sumula).filter(
            Gol.jogador_id == self.id,
            Sumula.partida_id.in_(partidas_ids),
            Gol.contra == False
        ).count()

        assistencias = Gol.query.join(Sumula).filter(
            Gol.assistencia_id == self.id,
            Sumula.partida_id.in_(partidas_ids)
        ).count()

        cleansheets = CleanSheet.query.join(Sumula).filter(
            CleanSheet.jogador_id == self.id,
            Sumula.partida_id.in_(partidas_ids)
        ).count()

        gols_contra = Gol.query.join(Sumula).filter(
            Gol.jogador_id == self.id,
            Sumula.partida_id.in_(partidas_ids),
            Gol.contra == True
        ).count()

        amarelos = Cartao.query.join(Sumula).filter(
            Cartao.jogador_id == self.id,
            Cartao.tipo == 'amarelo',
            Sumula.partida_id.in_(partidas_ids)
        ).count()

        vermelhos = Cartao.query.join(Sumula).filter(
            Cartao.jogador_id == self.id,
            Cartao.tipo == 'vermelho',
            Sumula.partida_id.in_(partidas_ids)
        ).count()

        mvps = Sumula.query.filter(
            Sumula.mvp_id == self.id,
            Sumula.partida_id.in_(partidas_ids)
        ).count()

        return {
            "gols": gols,
            "assistencias": assistencias,
            "cleansheets": cleansheets,
            "gols_contra": gols_contra,
            "cartoes_amarelos": amarelos,
            "cartoes_vermelhos": vermelhos,
            "mvps": mvps
        }
    
    def estatisticas_ranking(self):
        estat = self.contar_estatisticas()
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao": self.posicao,
            "nacionalidade": self.nacionalidade,
            "gols": estat["gols"],
            "assistencias": estat["assistencias"],
            "cleansheets": estat["cleansheets"],
            "mvps": estat["mvps"]
        }

    def estatisticas_ranking_competicao(self, competicao_id):
        estat = self.contar_estatisticas_na_competicao(competicao_id)
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao": self.posicao,
            "nacionalidade": self.nacionalidade,
            "gols": estat["gols"],
            "assistencias": estat["assistencias"],
            "cleansheets": estat["cleansheets"],
            "mvps": estat["mvps"]
        }

    def dici(self):
        estatisticas = self.contar_estatisticas()
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao": self.posicao,
            "nacionalidade": self.nacionalidade,
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
    nacionalidade = dados.get("nacionalidade")
    times_ids = dados.get("times_ids", [])
    if not nome:
        return None, "Nome é obrigatório"
    if not posicao:
        return None, "Posição é obrigatória"

    novoJogador = Jogador(nome=nome, posicao=posicao, nacionalidade=nacionalidade)

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
    jogador.nacionalidade = dados.get("nacionalidade", jogador.nacionalidade)

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