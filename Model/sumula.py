from config import db
from Model.partida import Partida
from Model.jogador import Jogador

class Sumula(db.Model):
    __tablename__ = "sumula"

    id = db.Column(db.Integer, primary_key=True)
    partida_id = db.Column(db.Integer, db.ForeignKey("partida.id"), nullable=False)
    mvp_id = db.Column(db.Integer, db.ForeignKey("jogador.id"))

    partida = db.relationship("Partida", backref="sumula", uselist=False)
    mvp = db.relationship("Jogador")

    gols = db.relationship("Gol", backref="sumula", cascade="all, delete-orphan")
    cartoes = db.relationship("Cartao", backref="sumula", cascade="all, delete-orphan")

    def dici(self):
        return {
            "id": self.id,
            "partida_id": self.partida_id,
            "mvp": self.mvp.nome if self.mvp else None,
            "gols": [g.dici() for g in self.gols],
            "cartoes": [c.dici() for c in self.cartoes]
        }

class Gol(db.Model):
    __tablename__ = "gol"

    id = db.Column(db.Integer, primary_key=True)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    assistencia_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=True)
    contra = db.Column(db.Boolean, default=False)

    sumula_id = db.Column(db.Integer, db.ForeignKey("sumula.id"), nullable=False)

    jogador = db.relationship("Jogador", foreign_keys=[jogador_id])
    assistencia = db.relationship("Jogador", foreign_keys=[assistencia_id])

    def dici(self):
        if self.contra:
            return {
                "tipo": "contra",
                "autor": self.jogador.nome
            }
        return {
            "tipo": "normal",
            "autor": self.jogador.nome,
            "assistencia": self.assistencia.nome if self.assistencia else None
        }


class Cartao(db.Model):
    __tablename__ = "cartao"

    id = db.Column(db.Integer, primary_key=True)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # amarelo/vermelho

    sumula_id = db.Column(db.Integer, db.ForeignKey("sumula.id"), nullable=False)
    jogador = db.relationship("Jogador")

    def dici(self):
        return {
            "jogador": self.jogador.nome,
            "tipo": self.tipo
        }

def ListarSumulas():
    return Sumula.query.all()

def BuscarSumulaPorId(sumula_id):
    return Sumula.query.get(sumula_id)

def CriarSumula(dados):
    partida = Partida.query.get(dados.get("partida_id"))
    if not partida:
        return None, "Partida não encontrada"

    if hasattr(partida, "sumula") and partida.sumula:
        return None, "Súmula já registrada para esta partida"

    sumula = Sumula(partida_id=partida.id)

    mvp_id = dados.get("mvp_id")
    if mvp_id:
        sumula.mvp = Jogador.query.get(mvp_id)

    for g in dados.get("gols", []):
        jogador = Jogador.query.get(g.get("jogador_id"))
        if not jogador:
            continue
        gol = Gol(
            jogador=jogador,
            assistencia=Jogador.query.get(g.get("assistencia_id")) if g.get("assistencia_id") else None,
            contra=g.get("contra", False)
        )
        sumula.gols.append(gol)

    for c in dados.get("cartoes", []):
        jogador = Jogador.query.get(c.get("jogador_id"))
        if not jogador:
            continue
        cartao = Cartao(jogador=jogador, tipo=c.get("tipo", "amarelo"))
        sumula.cartoes.append(cartao)

    db.session.add(sumula)
    db.session.commit()
    return sumula, None

def AtualizarSumula(sumula_id, dados):
    sumula = Sumula.query.get(sumula_id)
    if not sumula:
        return None, "Súmula não encontrada"

    if "mvp_id" in dados:
        sumula.mvp = Jogador.query.get(dados["mvp_id"])

    if "gols" in dados:
        sumula.gols = []
        for g in dados["gols"]:
            jogador = Jogador.query.get(g.get("jogador_id"))
            if not jogador:
                continue
            gol = Gol(
                jogador=jogador,
                assistencia=Jogador.query.get(g.get("assistencia_id")) if g.get("assistencia_id") else None,
                contra=g.get("contra", False)
            )
            sumula.gols.append(gol)

    if "cartoes" in dados:
        sumula.cartoes = []
        for c in dados["cartoes"]:
            jogador = Jogador.query.get(c.get("jogador_id"))
            if not jogador:
                continue
            cartao = Cartao(jogador=jogador, tipo=c.get("tipo", "amarelo"))
            sumula.cartoes.append(cartao)

    db.session.commit()
    return sumula, None

def DeletarSumula(sumula_id):
    sumula = Sumula.query.get(sumula_id)
    if not sumula:
        return False, "Súmula não encontrada"
    db.session.delete(sumula)
    db.session.commit()
    return True, None