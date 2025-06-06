from flask import request
from config import db

class Grupo(db.Model):
    __tablename__ = "grupo"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(2), nullable=False)
    liga_id = db.Column(db.Integer, db.ForeignKey('liga.id'), nullable=True)
    
    times = db.relationship("Time", back_populates="grupo", lazy=True)
    liga = db.relationship("Liga", back_populates="grupos")
    partidas = db.relationship("Partida", back_populates="grupo")
    
    def __init__(self, nome, liga_id):
        self.nome = nome
        self.liga_id = liga_id
        
    def __repr__(self):
        return self.nome
    
    def dici(self):
        classificacao = self.calcular_classificacao()
        
        return {
            "id": self.id,
            "nome": self.nome,
            "liga_id": self.liga_id,
            "times": [t.dici() for t in self.times],
            "classificacao": list(classificacao.values())
        }
    
    def calcular_classificacao(self):
        classificacao = {
            time.id: {
                "id": time.id,
                "nome": time.nome,
                "pontos": 0,
                "vitorias": 0,
                "empates": 0,
                "derrotas": 0,
                "gols_marcados": 0,
                "gols_sofridos": 0,
                "saldo_de_gols": 0,
                "jogos": 0
            } for time in self.times
        }
        for partida in self.partidas:
            if partida.gols_casa is None or partida.gols_fora is None:
                continue

            time_casa = partida.time_casa
            time_fora = partida.time_fora

            classificacao[time_casa.id]["jogos"] += 1
            classificacao[time_fora.id]["jogos"] += 1

            self._atualizar_estatisticas(
                classificacao,
                time_casa.id,
                time_fora.id,
                partida.gols_casa,
                partida.gols_fora
            )

        return self._ordenar_classificacao(classificacao)

    def _atualizar_estatisticas(self, classificacao, casa_id, fora_id, gols_casa, gols_fora):
        classificacao[casa_id]["gols_marcados"] += gols_casa
        classificacao[casa_id]["gols_sofridos"] += gols_fora
        
        classificacao[fora_id]["gols_marcados"] += gols_fora
        classificacao[fora_id]["gols_sofridos"] += gols_casa

        if gols_casa > gols_fora:
            classificacao[casa_id]["pontos"] += 3
            classificacao[casa_id]["vitorias"] += 1
            classificacao[fora_id]["derrotas"] += 1
        elif gols_fora > gols_casa:
            classificacao[fora_id]["pontos"] += 3
            classificacao[fora_id]["vitorias"] += 1
            classificacao[casa_id]["derrotas"] += 1
        else:
            classificacao[casa_id]["pontos"] += 1
            classificacao[fora_id]["pontos"] += 1
            classificacao[casa_id]["empates"] += 1
            classificacao[fora_id]["empates"] += 1

    def _ordenar_classificacao(self, classificacao):
        for dados in classificacao.values():
            dados["saldo_de_gols"] = dados["gols_marcados"] - dados["gols_sofridos"]
        
        return sorted(
            classificacao.values(),
            key=lambda x: (-x["pontos"], -x["vitorias"], -x["saldo_de_gols"], -x["gols_marcados"])
        )

    def dici(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "liga_id": self.liga_id,
            "times": [t.dici() for t in self.times],
            "classificacao": self.calcular_classificacao()
        }

def ListarGrupos():
    return Grupo.query.all()

def ListarGrupoPorId(id_grupo):
    return Grupo.query.get(id_grupo)

def CriarGrupo(dados):
    if not dados.get('nome'):
        return None, "Nome do grupo é obrigatório"
    
    if not dados.get('liga_id'):
        return None, "ID da liga é obrigatório"
    
    novo_grupo = Grupo(
        nome=dados['nome'],
        liga_id=dados['liga_id']
    )
        
    db.session.add(novo_grupo)
    db.session.commit()
    return novo_grupo, None

def AtualizarGrupo(id_grupo, dados):
    grupo = Grupo.query.get(id_grupo)
    if not grupo:
        return None, "Grupo não encontrado"
    
    if 'nome' in dados:
        grupo.nome = dados['nome']
            
    if 'liga_id' in dados:
        grupo.liga_id = dados['liga_id']
            
    db.session.commit()
    return grupo, None

def DeletarGrupo(id_grupo):
    grupo = Grupo.query.get(id_grupo)
    if not grupo:
        return False, "Grupo não encontrado"
    
    db.session.delete(grupo)
    db.session.commit()
    return True, None

def ObterClassificacaoPorGrupoId(id_grupo):
    grupo = Grupo.query.get(id_grupo)
    if not grupo:
        return None, "Grupo não encontrado"
    
    try:
        classificacao = grupo.calcular_classificacao()
        return classificacao, None
    except Exception as e:
        return None, f"Erro ao calcular classificação: {str(e)}"