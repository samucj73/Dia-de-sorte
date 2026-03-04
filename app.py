# =========================================================
# DIA DE SORTE INTELIGENTE — MOTOR HÍBRIDO ELITE
# Top-31 por frequência | Lógica Oculta Integrada
# =========================================================

import streamlit as st
import pandas as pd
import random
import json
from pathlib import Path
from abc import ABC, abstractmethod

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

# =========================================================
# CACHE
# =========================================================

@st.cache_data(ttl=3600)
def carregar_sorteios_cacheados(qtd):
    return baixar_ultimos_sorteios(qtd)

# =========================================================
# SERVIÇO DE FREQUÊNCIA TOP-31
# =========================================================

class FrequenciaTop31Service:
    def __init__(self, sorteios, janela=30):
        self.sorteios = sorteios[:janela]
        self.frequencias = self._calcular()

    def _calcular(self):
        contador = {i: 0 for i in range(1, 32)}
        for s in self.sorteios:
            for d in map(int, s["dezenas"]):
                contador[d] += 1
        return contador

    def ranking(self):
        return sorted(
            self.frequencias.items(),
            key=lambda x: x[1],
            reverse=True
        )

    def zonas(self):
        ranking = self.ranking()
        return {
            "alta": [n for n, _ in ranking[:10]],
            "media": [n for n, _ in ranking[10:21]],
            "baixa": [n for n, _ in ranking[21:]]
        }

    def pesos(self):
        return list(self.frequencias.keys()), list(self.frequencias.values())

# =========================================================
# MOTOR OCULTO
# =========================================================

class MotorOcultoTop31:
    def __init__(self, sorteios):
        self.freq = FrequenciaTop31Service(sorteios)
        self.zonas = self.freq.zonas()
        self.numeros, self.pesos = self.freq.pesos()

    def gerar_cartao(self):
        cartao = set()

        cartao.update(random.sample(self.zonas["alta"], 3))
        cartao.update(random.sample(self.zonas["media"], 2))
        cartao.update(random.sample(self.zonas["baixa"], 2))

        while len(cartao) < 7:
            cartao.add(
                random.choices(self.numeros, weights=self.pesos, k=1)[0]
            )

        return sorted(cartao)

# =========================================================
# FILTRO
# =========================================================

class FiltroEstatistico:
    @staticmethod
    def valido(cartao):
        soma = sum(cartao)
        pares = sum(1 for d in cartao if d % 2 == 0)
        return 70 <= soma <= 95 and pares in (3, 4)

# =========================================================
# ESTRATÉGIAS
# =========================================================

class Estrategia(ABC):
    nome: str

    @abstractmethod
    def gerar(self, qtd, sorteios):
        pass

class EstrategiaOtimizada(Estrategia):
    nome = "Otimizada"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_otimizados_adaptativo(qtd, sorteios)

class EstrategiaEliteHibrida(Estrategia):
    nome = "Elite Híbrida (Otimizada + Oculta)"

    def gerar(self, qtd, sorteios):
        motor = MotorOcultoTop31(sorteios)
        cartoes = []

        while len(cartoes) < qtd:
            dezenas = motor.gerar_cartao()
            if FiltroEstatistico.valido(dezenas):
                cartoes.append({
                    "dezenas": dezenas,
                    "mesSorte": random.choice([
                        s["mesSorte"] for s in sorteios
                    ])
                })
        return cartoes

class EstrategiaInversa(Estrategia):
    nome = "Inversa"
    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos(qtd, sorteios)

class EstrategiaInversaInvertida(Estrategia):
    nome = "Inversa Invertida"
    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos_invertidos(qtd, sorteios)

# =========================================================
# STREAMLIT
# =========================================================

class StreamlitApp:
    def run(self):
        st.set_page_config("Dia de Sorte Inteligente", layout="wide")
        st.title("💡 Dia de Sorte — Motor Elite")

        qtd_concursos = st.slider("Concursos analisados", 30, 300, 100)
        sorteios = carregar_sorteios_cacheados(qtd_concursos)

        abas = st.tabs(["🎯 Gerar", "📊 Análises", "✅ Conferir"])

        with abas[0]:
            qtd = st.number_input("Qtd cartões", 1, 20, 5)

            estrategia = st.selectbox(
                "Estratégia",
                [
                    EstrategiaEliteHibrida(),
                    EstrategiaOtimizada(),
                    EstrategiaInversa(),
                    EstrategiaInversaInvertida()
                ],
                format_func=lambda e: e.nome
            )

            if st.button("Gerar"):
                cartoes = estrategia.gerar(qtd, sorteios)
                st.session_state["cartoes"] = cartoes

                for i, c in enumerate(cartoes, 1):
                    st.write(f"🃏 {i} → {c['dezenas']} | Mês: {c['mesSorte']}")

        with abas[2]:
            if st.button("Conferir"):
                resultados = conferir_cartoes(
                    st.session_state.get("cartoes", [])
                )
                for r in resultados:
                    st.write(r)

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    StreamlitApp().run()
