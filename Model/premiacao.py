from config import db
from Model.jogador import Jogador
from Model.competicao import Competicao
from Model.time import Time

top_gk = db.Table('top_gk',
    db.Column('premiacao_id', db.Integer, db.ForeignKey('premiacao.id')),
    db.Column('jogador_id', db.Integer, db.ForeignKey('jogador.id'))
)

top_zag = db.Table('top_zag',
    db.Column('premiacao_id', db.Integer, db.ForeignKey('premiacao.id')),
    db.Column('jogador_id', db.Integer, db.ForeignKey('jogador.id'))
)

top_mid = db.Table('top_mid',
    db.Column('premiacao_id', db.Integer, db.ForeignKey('premiacao.id')),
    db.Column('jogador_id', db.Integer, db.ForeignKey('jogador.id'))
)

top_atk = db.Table('top_atk',
    db.Column('premiacao_id', db.Integer, db.ForeignKey('premiacao.id')),
    db.Column('jogador_id', db.Integer, db.ForeignKey('jogador.id'))
)


class Premiacao(db.Model):
    __tablename__ = "premiacao"

    id = db.Column(db.Integer, primary_key=True)
    competicao_id = db.Column(db.Integer, db.ForeignKey("competicao.id"), nullable=False)

    mvp_id = db.Column(db.Integer, db.ForeignKey("jogador.id"))
    artilheiro_id = db.Column(db.Integer, db.ForeignKey("jogador.id"))
    luva_de_ouro_id = db.Column(db.Integer, db.ForeignKey("jogador.id"))
    revelacao_id = db.Column(db.Integer, db.ForeignKey("jogador.id"))
    campeao_id = db.Column(db.Integer, db.ForeignKey("time.id"))

    mvp = db.relationship("Jogador", foreign_keys=[mvp_id])
    artilheiro = db.relationship("Jogador", foreign_keys=[artilheiro_id])
    luva_de_ouro = db.relationship("Jogador", foreign_keys=[luva_de_ouro_id])
    revelacao = db.relationship("Jogador", foreign_keys=[revelacao_id])
    campeao = db.relationship("Time", foreign_keys=[campeao_id])

    top_gk = db.relationship("Jogador", secondary=top_gk, backref="premiacoes_gk")
    top_zag = db.relationship("Jogador", secondary=top_zag, backref="premiacoes_zag")
    top_mid = db.relationship("Jogador", secondary=top_mid, backref="premiacoes_mid")
    top_atk = db.relationship("Jogador", secondary=top_atk, backref="premiacoes_atk")

    competicao = db.relationship("Competicao", back_populates="premiacao")

    def __init__(self, competicao):
        self.competicao = competicao

    def dici(self):
        return {
            "id": self.id,
            "competicao": self.competicao_id,
            "mvp": self.mvp.nome if self.mvp else None,
            "artilheiro": self.artilheiro.nome if self.artilheiro else None,
            "luva_de_ouro": self.luva_de_ouro.nome if self.luva_de_ouro else None,
            "revelacao": self.revelacao.nome if self.revelacao else None,
            "top_gk": [j.nome for j in self.top_gk],
            "top_zag": [j.nome for j in self.top_zag],
            "top_mid": [j.nome for j in self.top_mid],
            "top_atk": [j.nome for j in self.top_atk],
            "campeao": self.campeao.nome if self.campeao else None
        }


def ListarPremiacoes():
    return Premiacao.query.all()

def BuscarPremiacaoPorId(premiacao_id):
    return Premiacao.query.get(premiacao_id)

def CriarPremiacao(dados):
    competicao = Competicao.query.get(dados.get("competicao_id"))
    if not competicao:
        return None, "Competição não encontrada"

    premiacao = Premiacao(competicao=competicao)

    if dados.get("campeao_id"):
        campeao = Time.query.get(dados["campeao_id"])
        if not campeao:
            return None, "Time campeão não encontrado"
        premiacao.campeao = campeao

    def buscar_jogador(campo):
        return Jogador.query.get(dados.get(campo)) if dados.get(campo) else None

    premiacao.mvp = buscar_jogador("mvp_id")
    premiacao.artilheiro = buscar_jogador("artilheiro_id")
    premiacao.luva_de_ouro = buscar_jogador("luva_de_ouro_id")
    premiacao.revelacao = buscar_jogador("revelacao_id")

    def adicionar_lista(nome_lista, lista_ids):
        for jogador_id in lista_ids:
            jogador = Jogador.query.get(jogador_id)
            if jogador:
                getattr(premiacao, nome_lista).append(jogador)

    adicionar_lista("top_gk", dados.get("top_gk_ids", []))
    adicionar_lista("top_zag", dados.get("top_zag_ids", []))
    adicionar_lista("top_mid", dados.get("top_mid_ids", []))
    adicionar_lista("top_atk", dados.get("top_atk_ids", []))

    db.session.add(premiacao)
    db.session.commit()
    return premiacao, None

def AtualizarPremiacao(premiacao_id, dados):
    premiacao = Premiacao.query.get(premiacao_id)
    if not premiacao:
        return None, "Premiação não encontrada"

    def buscar_jogador(campo):
        return Jogador.query.get(dados.get(campo)) if dados.get(campo) else None

    premiacao.mvp = buscar_jogador("mvp_id") or premiacao.mvp
    premiacao.artilheiro = buscar_jogador("artilheiro_id") or premiacao.artilheiro
    premiacao.luva_de_ouro = buscar_jogador("luva_de_ouro_id") or premiacao.luva_de_ouro
    premiacao.revelacao = buscar_jogador("revelacao_id") or premiacao.revelacao

    if "campeao_id" in dados:
        novo_campeao = Time.query.get(dados["campeao_id"])
        if not novo_campeao:
            return None, "Time campeão não encontrado"
        premiacao.campeao = novo_campeao

    def atualizar_lista(nome_lista, lista_ids):
        nova_lista = []
        for jogador_id in lista_ids:
            jogador = Jogador.query.get(jogador_id)
            if jogador:
                nova_lista.append(jogador)
        setattr(premiacao, nome_lista, nova_lista)

    if "top_gk_ids" in dados:
        atualizar_lista("top_gk", dados["top_gk_ids"])
    if "top_zag_ids" in dados:
        atualizar_lista("top_zag", dados["top_zag_ids"])
    if "top_mid_ids" in dados:
        atualizar_lista("top_mid", dados["top_mid_ids"])
    if "top_atk_ids" in dados:
        atualizar_lista("top_atk", dados["top_atk_ids"])

    db.session.commit()
    return premiacao, None

def DeletarPremiacao(premiacao_id):
    premiacao = Premiacao.query.get(premiacao_id)
    if not premiacao:
        return False, "Premiação não encontrada"

    db.session.delete(premiacao)
    db.session.commit()
    return True, None