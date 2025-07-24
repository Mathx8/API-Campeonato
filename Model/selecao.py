from config import db
from Model.jogador import Jogador
from Model.competicao import Competicao

class SelecaoRodada(db.Model):
    __tablename__ = "selecao_rodada"
    id = db.Column(db.Integer, primary_key=True)
    rodada = db.Column(db.String(20), nullable=False)
    competicao_id = db.Column(db.Integer, db.ForeignKey("competicao.id"), nullable=False)
    observacoes = db.Column(db.Text)

    jogadores = db.relationship("JogadorSelecao", backref="selecao", cascade="all, delete-orphan")

    def dici(self):
        return {
            "id": self.id,
            "rodada": self.rodada,
            "competicao_id": self.competicao_id,
            "competicao": Competicao.query.get(self.competicao_id).nome if self.competicao_id else None,
            "observacoes": self.observacoes,
            "jogadores":  [js.dici() for js in self.jogadores]
        }

class JogadorSelecao(db.Model):
    __tablename__ = "jogador_selecao"
    id = db.Column(db.Integer, primary_key=True)
    selecao_id = db.Column(db.Integer, db.ForeignKey("selecao_rodada.id", ondelete="CASCADE"), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    categoria = db.Column(db.String(10), nullable=False)

    jogador = db.relationship("Jogador")

    def dici(self):
        time_da_competicao = next(
            (
                {
                    "id": t.id,
                    "nome": t.nome,
                    "competicao": {
                        "id": t.competicao.id,
                        "nome": t.competicao.nome
                    } if t.competicao else None
                }
                for t in self.jogador.times
                if t.competicao and t.competicao.id == self.selecao.competicao_id
            ),
            None
        )
        
        return {
            "id": self.jogador.id,
            "nome": self.jogador.nome,
            "categoria": self.categoria,
            "nacionalidade": self.jogador.nacionalidade,
            "time": time_da_competicao
        }


def adicionar_jogadores(selecao, categoria, lista_ids):
    for jogador_id in lista_ids:
        jogador = Jogador.query.get(jogador_id)
        if jogador:
            js = JogadorSelecao(
                jogador=jogador,
                categoria=categoria
            )
            selecao.jogadores.append(js)

def atualizar_jogadores(selecao, categoria, lista_ids):
    selecao.jogadores = [j for j in selecao.jogadores if j.categoria != categoria]
    adicionar_jogadores(selecao, categoria, lista_ids)

def ListarSelecoes():
    return SelecaoRodada.query.all()

def BuscarSelecaoPorId(selecao_id):
    return SelecaoRodada.query.get(selecao_id)

def CriarSelecao(dados):
    competicao = Competicao.query.get(dados.get("competicao_id"))
    if not competicao:
        return None, "Competição não encontrada"

    selecao = SelecaoRodada(
        rodada=dados.get("rodada"),
        competicao_id=competicao.id,
        observacoes=dados.get("observacoes", "")
    )

    adicionar_jogadores(selecao, "GK", dados.get("gk", []))
    adicionar_jogadores(selecao, "ZAG", dados.get("zag", []))
    adicionar_jogadores(selecao, "MID", dados.get("mid", []))
    adicionar_jogadores(selecao, "ATK", dados.get("atk", []))

    db.session.add(selecao)
    db.session.commit()
    return selecao, None

def AtualizarSelecao(selecao_id, dados):
    selecao = SelecaoRodada.query.get(selecao_id)
    if not selecao:
        return None, "Seleção não encontrada"

    if "rodada" in dados:
        selecao.rodada = dados["rodada"]

    if "competicao_id" in dados:
        nova_competicao = Competicao.query.get(dados["competicao_id"])
        if not nova_competicao:
            return None, "Competição não encontrada"
        selecao.competicao_id = nova_competicao.id

    if "observacoes" in dados:
        selecao.observacoes = dados["observacoes"]

    if "gk" in dados:
        atualizar_jogadores(selecao, "GK", dados["gk"])
    if "zag" in dados:
        atualizar_jogadores(selecao, "ZAG", dados["zag"])
    if "mid" in dados:
        atualizar_jogadores(selecao, "MID", dados["mid"])
    if "atk" in dados:
        atualizar_jogadores(selecao, "ATK", dados["atk"])

    db.session.commit()
    return selecao, None

def DeletarSelecao(selecao_id):
    selecao = SelecaoRodada.query.get(selecao_id)
    if not selecao:
        return False, "Seleção não encontrada"

    db.session.delete(selecao)
    db.session.commit()
    return True, None