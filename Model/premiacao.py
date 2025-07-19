from config import db
from Model.jogador import Jogador
from Model.competicao import Competicao
from Model.time import Time

class TopJogadorPremiacao(db.Model):
    __tablename__ = "top_jogador_premiacao"

    id = db.Column(db.Integer, primary_key=True)
    premiacao_id = db.Column(db.Integer, db.ForeignKey("premiacao.id"), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    categoria = db.Column(db.String(10), nullable=False)
    posicao = db.Column(db.Integer, nullable=False)

    premiacao = db.relationship("Premiacao", back_populates="tops")
    jogador = db.relationship("Jogador")

    __table_args__ = (
        db.UniqueConstraint('premiacao_id', 'categoria', 'posicao', name='_unique_top_position'),
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

    competicao = db.relationship("Competicao", back_populates="premiacao")
    tops = db.relationship("TopJogadorPremiacao", back_populates="premiacao", cascade="all, delete-orphan")

    def __init__(self, competicao):
        self.competicao = competicao

    def dici(self):
        def extrair_top(categoria):
            return sorted([
                {"nome": t.jogador.nome, "posicao": t.posicao} for t in self.tops if t.categoria == categoria
            ], key=lambda x: x["posicao"])

        return {
            "id": self.id,
            "competicao": self.competicao_id,
            "mvp": self.mvp.nome if self.mvp else None,
            "artilheiro": self.artilheiro.nome if self.artilheiro else None,
            "luva_de_ouro": self.luva_de_ouro.nome if self.luva_de_ouro else None,
            "revelacao": self.revelacao.nome if self.revelacao else None,
            "top_gk": extrair_top("GK"),
            "top_zag": extrair_top("ZAG"),
            "top_mid": extrair_top("MID"),
            "top_atk": extrair_top("ATK"),
            "campeao": self.campeao.nome if self.campeao else None
        }

def adicionar_tops(premiacao, categoria, lista):
    for item in lista:
        jogador = Jogador.query.get(item["jogador_id"])
        if jogador:
            top = TopJogadorPremiacao(
                jogador=jogador,
                categoria=categoria,
                posicao=item["posicao"]
            )
            premiacao.tops.append(top)

def atualizar_tops(premiacao, categoria, lista):
    premiacao.tops = [t for t in premiacao.tops if t.categoria != categoria]
    adicionar_tops(premiacao, categoria, lista)

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

    adicionar_tops(premiacao, "GK", dados.get("top_gk", []))
    adicionar_tops(premiacao, "ZAG", dados.get("top_zag", []))
    adicionar_tops(premiacao, "MID", dados.get("top_mid", []))
    adicionar_tops(premiacao, "ATK", dados.get("top_atk", []))

    db.session.add(premiacao)
    db.session.commit()
    return premiacao, None

def AtualizarPremiacao(premiacao_id, dados):
    premiacao = Premiacao.query.get(premiacao_id)
    if not premiacao:
        return None, "Premiação não encontrada"

    def buscar_jogador(campo):
        return Jogador.query.get(dados.get(campo)) if dados.get(campo) else None

    if "mvp_id" in dados:
        premiacao.mvp = buscar_jogador("mvp_id")
    if "artilheiro_id" in dados:
        premiacao.artilheiro = buscar_jogador("artilheiro_id")
    if "luva_de_ouro_id" in dados:
        premiacao.luva_de_ouro = buscar_jogador("luva_de_ouro_id")
    if "revelacao_id" in dados:
        premiacao.revelacao = buscar_jogador("revelacao_id")

    if "campeao_id" in dados:
        novo_campeao = Time.query.get(dados["campeao_id"])
        if not novo_campeao:
            return None, "Time campeão não encontrado"
        premiacao.campeao = novo_campeao

    if "top_gk" in dados:
        atualizar_tops(premiacao, "GK", dados["top_gk"])
    if "top_zag" in dados:
        atualizar_tops(premiacao, "ZAG", dados["top_zag"])
    if "top_mid" in dados:
        atualizar_tops(premiacao, "MID", dados["top_mid"])
    if "top_atk" in dados:
        atualizar_tops(premiacao, "ATK", dados["top_atk"])

    db.session.commit()
    return premiacao, None

def DeletarPremiacao(premiacao_id):
    premiacao = Premiacao.query.get(premiacao_id)
    if not premiacao:
        return False, "Premiação não encontrada"

    db.session.delete(premiacao)
    db.session.commit()
    return True, None