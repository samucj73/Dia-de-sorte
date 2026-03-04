# =========================================================
# DIA DE SORTE INTELIGENTE - CÓDIGO PRINCIPAL
# Motor Elite Híbrido | Top-31 por Frequência
# =========================================================

import streamlit as st
import pandas as pd
import random
import json
from pathlib import Path
from abc import ABC, abstractmethod

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

# =========================================================
# CACHE
# =========================================================

@st.cache_data(ttl=3600)
def carregar_sorteios_cacheados(qtd):
    return baixar_ultimos_sorteios(qtd)

# =========================================================
# SERVIÇO DE ESTATÍSTICAS
# =========================================================

class EstatisticasService:
    def __init__(self, sorteios):
        self.sorteios = sorteios

    def dezenas(self): return frequencia_dezenas(self.sorteios)
    def meses(self): return frequencia_meses(self.sorteios)
    def pares(self): return pares_impares(self.sorteios)
    def soma(self): return soma_dezenas(self.sorteios)
    def sequencias(self): return sequencias_consecutivas(self.sorteios)
    def repeticoes(self): return repeticao_entre_concursos(self.sorteios)

# =========================================================
# MOTOR OCULTO TOP-31
# =========================================================

class FrequenciaTop31Service:
    def __init__(self, sorteios, janela=30):
        self.sorteios = sorteios[:janela]
        self.freq = self._calcular()

    def _calcular(self):
        cont = {i: 0 for i in range(1, 32)}
        for s in self.sorteios:
            for d in map(int, s["dezenas"]):
                cont[d] += 1
        return cont

    def ranking(self):
        return sorted(self.freq.items(), key=lambda x: x[1], reverse=True)

    def zonas(self):
        r = self.ranking()
        return {
            "alta": [n for n, _ in r[:10]],
            "media": [n for n, _ in r[10:21]],
            "baixa": [n for n, _ in r[21:]]
        }

    def pesos(self):
        return list(self.freq.keys()), list(self.freq.values())

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
# FILTRO ESTATÍSTICO
# =========================================================

class FiltroEstatistico:
    @staticmethod
    def valido(dezenas):
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)
        return 70 <= soma <= 95 and pares in (3, 4)

# =========================================================
# STRATEGY PATTERN
# =========================================================

class Estrategia(ABC):
    nome: str

    @abstractmethod
    def gerar(self, qtd, sorteios):
        pass

class EstrategiaEliteHibrida(Estrategia):
    nome = "Elite Híbrida (Top-31 Oculta)"

    def gerar(self, qtd, sorteios):
        motor = MotorOcultoTop31(sorteios)
        cartoes = []

        while len(cartoes) < qtd:
            dezenas = motor.gerar_cartao()
            if FiltroEstatistico.valido(dezenas):
                cartoes.append({
                    "dezenas": dezenas,
                    "mesSorte": random.choice([s["mesSorte"] for s in sorteios])
                })
        return cartoes

class EstrategiaOtimizada(Estrategia):
    nome = "Otimizada Clássica"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_otimizados_adaptativo(qtd, sorteios)

class EstrategiaInversa(Estrategia):
    nome = "Inversa"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos(qtd, sorteios)

class EstrategiaInversaInvertida(Estrategia):
    nome = "Inversa Invertida"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos_invertidos(qtd, sorteios)

# =========================================================
# STREAMLIT APP
# =========================================================

class StreamlitApp:
    def run(self):
        st.set_page_config(
            page_title="Dia de Sorte Inteligente",
            layout="wide"
        )

        st.title("💡 Dia de Sorte Inteligente — Motor Elite")

        qtd_concursos = st.slider(
            "Quantidade de concursos analisados",
            30, 300, 100
        )

        sorteios = carregar_sorteios_cacheados(qtd_concursos)

        # ---------- ÚLTIMO CONCURSO ----------
        if sorteios:
            ultimo = sorteios[0]
            st.info(
                f"🟢 Último concurso: {ultimo['concurso']} | "
                f"Data: {ultimo['data']} | "
                f"Dezenas: {', '.join(ultimo['dezenas'])} | "
                f"Mês da Sorte: {ultimo.get('mesSorte')}"
            )

        abas = st.tabs(["🎯 Gerar Cartões", "📊 Análises", "✅ Conferir"])

        # ---------- GERAR ----------
        with abas[0]:
            qtd = st.number_input("Quantidade de cartões", 1, 20, 5)

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

            if st.button("🎯 Gerar Cartões"):
                cartoes = estrategia.gerar(qtd, sorteios)
                st.session_state["cartoes"] = cartoes

                for i, c in enumerate(cartoes, 1):
                    st.write(f"🃏 {i} → {c['dezenas']} | Mês: {c['mesSorte']}")

        # ---------- ANÁLISES ----------
        with abas[1]:
            estat = EstatisticasService(sorteios)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔢 Frequência das Dezenas")
                st.dataframe(estat.dezenas(), use_container_width=True)

                st.subheader("🔁 Repetições")
                st.dataframe(estat.repeticoes(), use_container_width=True)

            with col2:
                st.subheader("📅 Frequência do Mês da Sorte")
                st.dataframe(estat.meses(), use_container_width=True)

                st.subheader("➕ Soma das Dezenas")
                st.dataframe(estat.soma(), use_container_width=True)

        # ---------- CONFERIR ----------
        with abas[2]:
            if st.button("✅ Conferir Cartões"):
                resultados = conferir_cartoes(
                    st.session_state.get("cartoes", [])
                )
                for r in resultados:
                    st.write(r)

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    StreamlitApp().run()
