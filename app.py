# =========================================================
# DIA DE SORTE INTELIGENTE - MOTOR ELITE
# OO | Strategy | Padrões Ocultos | Otimização | Streamlit
# =========================================================

import streamlit as st
import pandas as pd
import json
import random
from abc import ABC, abstractmethod
from pathlib import Path

# ===== IMPORTS DO ECOSSISTEMA =====
from diadesorte_api import baixar_ultimos_sorteios
from diadesorte_stats import (
    frequencia_dezenas, frequencia_meses,
    pares_impares, soma_dezenas,
    sequencias_consecutivas, repeticao_entre_concursos
)
from gerador_cartoes import gerar_cartoes_otimizados_adaptativo
from gerador_inverso import gerar_cartoes_inversos
from gerador_inverso_invertido import gerar_cartoes_inversos_invertidos
from conferidor import conferir_cartoes
from padroes_ocultos import PadroesOcultosService

# =========================================================
# CACHE
# =========================================================

@st.cache_data(ttl=3600)
def carregar_sorteios_cacheados(qtd):
    return baixar_ultimos_sorteios(qtd)

# =========================================================
# DATAFRAME
# =========================================================

def sorteios_para_dataframe(sorteios):
    return pd.DataFrame([{
        "concurso": s["concurso"],
        "data": s["data"],
        "dezenas": ",".join(s["dezenas"]),
        "mesSorte": s.get("mesSorte")
    } for s in sorteios])

# =========================================================
# SERVICES
# =========================================================

class SorteiosService:
    def __init__(self, qtd):
        self.sorteios = carregar_sorteios_cacheados(qtd)

    @property
    def ultimo(self):
        return self.sorteios[0] if self.sorteios else None

class EstatisticasService:
    def __init__(self, sorteios):
        self.sorteios = sorteios

    def dezenas(self): return frequencia_dezenas(self.sorteios)
    def meses(self): return frequencia_meses(self.sorteios)
    def pares_impares(self): return pares_impares(self.sorteios)
    def soma(self): return soma_dezenas(self.sorteios)
    def sequencias(self): return sequencias_consecutivas(self.sorteios)
    def repeticoes(self): return repeticao_entre_concursos(self.sorteios)

# =========================================================
# STRATEGY
# =========================================================

class Estrategia(ABC):
    nome: str

    @abstractmethod
    def gerar(self, qtd, sorteios):
        pass

class EstrategiaOtimizada(Estrategia):
    nome = "Otimizada"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_otimizados_adaptativo(
            qtd, sorteios, desempenho_minimo=4.5, max_tentativas=30000
        )

class EstrategiaOculta(Estrategia):
    nome = "Oculta (Blocos Estatísticos)"

    def gerar(self, qtd, sorteios):
        padroes = PadroesOcultosService(sorteios)
        cartoes = []

        while len(cartoes) < qtd:
            dezenas = set(padroes.sortear_bloco_oculto())
            while len(dezenas) < 7:
                dezenas.add(random.randint(1, 31))

            cartoes.append({
                "dezenas": [str(d).zfill(2) for d in sorted(dezenas)],
                "mesSorte": None
            })

        return cartoes

class EstrategiaHibridaElite(Estrategia):
    nome = "🔥 Híbrida Elite (Otimizada + Oculta)"

    def gerar(self, qtd, sorteios):
        padroes = PadroesOcultosService(sorteios)
        cartoes_finais = []
        tentativas = 0

        while len(cartoes_finais) < qtd and tentativas < 50000:
            tentativas += 1

            semente = padroes.sugerir_dezenas()

            candidatos = gerar_cartoes_otimizados_adaptativo(
                qtd=3,
                sorteios=sorteios,
                desempenho_minimo=4.0,
                max_tentativas=3000
            )

            for c in candidatos:
                dezenas = set(map(int, c["dezenas"]))
                dezenas.update(semente)

                while len(dezenas) > 7:
                    dezenas.remove(random.choice(tuple(dezenas)))
                while len(dezenas) < 7:
                    dezenas.add(random.randint(1, 31))

                cartao = {
                    "dezenas": [str(d).zfill(2) for d in sorted(dezenas)],
                    "mesSorte": c.get("mesSorte")
                }

                if FiltroEstatistico.valido(cartao):
                    cartoes_finais.append(cartao)

                if len(cartoes_finais) >= qtd:
                    break

        return cartoes_finais

class EstrategiaInversa(Estrategia):
    nome = "Inversa"
    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos(qtd, sorteios)

class EstrategiaInversaInvertida(Estrategia):
    nome = "Inversa Invertida"
    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos_invertidos(qtd, sorteios)

# =========================================================
# FILTRO
# =========================================================

class FiltroEstatistico:
    @staticmethod
    def valido(cartao):
        dezenas = list(map(int, cartao["dezenas"]))
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)

        return 70 <= soma <= 95 and pares in (3, 4)

# =========================================================
# GERADOR
# =========================================================

class GeradorService:
    def __init__(self, estrategia):
        self.estrategia = estrategia

    def gerar(self, qtd, sorteios):
        return [
            c for c in self.estrategia.gerar(qtd, sorteios)
            if FiltroEstatistico.valido(c)
        ]

# =========================================================
# AVALIAÇÃO / APRENDIZADO
# =========================================================

class AvaliadorService:
    def avaliar(self, cartoes):
        return conferir_cartoes(cartoes)

    def score_medio(self, resultados):
        return round(
            sum(r["acertos"] for r in resultados) / len(resultados), 2
        ) if resultados else 0

class AprendizadoService:
    FILE = Path("historico_aprendizado.json")

    def salvar(self, estrategia, score):
        dados = self._carregar()
        dados.setdefault(estrategia, []).append(score)
        self.FILE.write_text(json.dumps(dados, indent=2, ensure_ascii=False))

    def _carregar(self):
        return json.loads(self.FILE.read_text()) if self.FILE.exists() else {}

# =========================================================
# STREAMLIT
# =========================================================

class StreamlitApp:
    def run(self):
        st.set_page_config("Dia de Sorte Inteligente", layout="wide")
        st.title("💡 Dia de Sorte Inteligente — Motor Elite")

        qtd_concursos = st.slider("Concursos analisados", 30, 300, 100)
        sorteios = SorteiosService(qtd_concursos)

        if sorteios.ultimo:
            st.info(
                f"Último concurso {sorteios.ultimo['concurso']} | "
                f"{', '.join(sorteios.ultimo['dezenas'])} | "
                f"Mês: {sorteios.ultimo.get('mesSorte')}"
            )

        abas = st.tabs(["🎯 Gerar", "📊 Análises", "✅ Conferir"])

        with abas[0]:
            qtd = st.number_input("Quantidade de cartões", 1, 20, 5)

            estrategia = st.selectbox(
                "Estratégia",
                [
                    EstrategiaOtimizada(),
                    EstrategiaOculta(),
                    EstrategiaHibridaElite(),
                    EstrategiaInversa(),
                    EstrategiaInversaInvertida()
                ],
                format_func=lambda e: e.nome
            )

            if st.button("🎯 Gerar Cartões"):
                cartoes = GeradorService(estrategia).gerar(
                    qtd, sorteios.sorteios
                )
                st.session_state["cartoes"] = cartoes
                st.session_state["estrategia"] = estrategia.nome

                for i, c in enumerate(cartoes, 1):
                    st.write(f"🃏 {i} → {c['dezenas']}")

        with abas[1]:
            estat = EstatisticasService(sorteios.sorteios)
            st.subheader("Frequência das Dezenas")
            st.table(estat.dezenas())
            st.subheader("Meses da Sorte")
            st.table(estat.meses())

        with abas[2]:
            if st.button("✅ Conferir"):
                resultados = AvaliadorService().avaliar(
                    st.session_state.get("cartoes", [])
                )
                score = AvaliadorService().score_medio(resultados)
                AprendizadoService().salvar(
                    st.session_state.get("estrategia", "Desconhecida"),
                    score
                )
                st.metric("🎯 Score Médio", score)
                for r in resultados:
                    st.write(r)

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    StreamlitApp().run()
