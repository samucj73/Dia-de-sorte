# =========================================================
# DIA DE SORTE INTELIGENTE - ARQUIVO ÚNICO
# Orientação a Objetos | Produção | Download de Concursos
# =========================================================

import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod
import json
from pathlib import Path

# ===== IMPORTS DO SEU ECOSSISTEMA =====
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
# FUNÇÃO UTILITÁRIA – CONVERSÃO PARA DATAFRAME
# =========================================================

def sorteios_para_dataframe(sorteios):
    dados = []
    for s in sorteios:
        dados.append({
            "concurso": s.get("concurso"),
            "data": s.get("data"),
            "dezenas": ",".join(s.get("dezenas", [])),
            "mesSorte": s.get("mesSorte")
        })
    return pd.DataFrame(dados)


# =========================================================
# SERVIÇO DE SORTEIOS (CACHE + DADOS)
# =========================================================

class SorteiosService:
    def __init__(self, quantidade: int):
        self.quantidade = quantidade
        self.sorteios = self._carregar()

    @st.cache_data(ttl=3600)
    def _carregar(self):
        return baixar_ultimos_sorteios(self.quantidade)

    @property
    def ultimo(self):
        return self.sorteios[0] if self.sorteios else None


# =========================================================
# ESTATÍSTICAS
# =========================================================

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
# ESTRATÉGIAS (STRATEGY PATTERN)
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


class EstrategiaInversa(Estrategia):
    nome = "Inversa"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos(qtd, sorteios)


class EstrategiaInversaInvertida(Estrategia):
    nome = "Inversa Invertida"

    def gerar(self, qtd, sorteios):
        return gerar_cartoes_inversos_invertidos(qtd, sorteios)


# =========================================================
# FILTROS INTELIGENTES (ASSERTIVIDADE)
# =========================================================

class FiltroEstatistico:
    @staticmethod
    def valido(cartao):
        dezenas = list(map(int, cartao["dezenas"]))
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)

        if not (70 <= soma <= 95):
            return False
        if pares not in (3, 4):
            return False

        return True


# =========================================================
# GERADOR CENTRAL
# =========================================================

class GeradorService:
    def __init__(self, estrategia: Estrategia):
        self.estrategia = estrategia

    def gerar(self, qtd, sorteios):
        cartoes = self.estrategia.gerar(qtd, sorteios)
        return [c for c in cartoes if FiltroEstatistico.valido(c)]


# =========================================================
# AVALIAÇÃO + AUTO-APRENDIZADO
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
        if self.FILE.exists():
            return json.loads(self.FILE.read_text())
        return {}


# =========================================================
# STREAMLIT APP
# =========================================================

class StreamlitApp:
    def run(self):
        st.set_page_config(
            page_title="Dia de Sorte Inteligente",
            layout="wide"
        )

        st.title("💡 Dia de Sorte Inteligente")

        qtd_concursos = st.slider(
            "Quantos concursos deseja analisar?",
            30, 300, 100
        )

        sorteios = SorteiosService(qtd_concursos)

        # ---------- DOWNLOAD DOS CONCURSOS ----------
        with st.expander("⬇️ Download dos concursos capturados"):
            if sorteios.sorteios:
                df = sorteios_para_dataframe(sorteios.sorteios)

                st.download_button(
                    label="📥 Baixar concursos em CSV",
                    data=df.to_csv(index=False),
                    file_name="concursos_dia_de_sorte.csv",
                    mime="text/csv"
                )

                st.download_button(
                    label="📥 Baixar concursos em JSON",
                    data=df.to_json(
                        orient="records",
                        force_ascii=False,
                        indent=2
                    ),
                    file_name="concursos_dia_de_sorte.json",
                    mime="application/json"
                )
            else:
                st.warning("Nenhum concurso disponível para download.")

        # ---------- ÚLTIMO CONCURSO ----------
        if sorteios.ultimo:
            st.info(
                f"Último concurso: {sorteios.ultimo['concurso']} | "
                f"Dezenas: {', '.join(sorteios.ultimo['dezenas'])} | "
                f"Mês da Sorte: {sorteios.ultimo.get('mesSorte')}"
            )

        abas = st.tabs(["🎯 Gerar Cartões", "📊 Análises", "✅ Conferir"])

        # ---------- ABA GERAR ----------
        with abas[0]:
            qtd = st.number_input("Quantidade de cartões", 1, 20, 5)

            estrategia = st.selectbox(
                "Estratégia",
                [
                    EstrategiaOtimizada(),
                    EstrategiaInversa(),
                    EstrategiaInversaInvertida()
                ],
                format_func=lambda e: e.nome
            )

            if st.button("🎯 Gerar Cartões"):
                gerador = GeradorService(estrategia)
                cartoes = gerador.gerar(qtd, sorteios.sorteios)

                st.session_state["cartoes"] = cartoes
                st.session_state["estrategia"] = estrategia.nome

                for i, c in enumerate(cartoes, 1):
                    st.write(f"🃏 {i} → {c['dezenas']} | Mês: {c['mesSorte']}")

        # ---------- ABA ANÁLISES ----------
        with abas[1]:
            estat = EstatisticasService(sorteios.sorteios)

            st.subheader("🔥 Frequência das Dezenas")
            st.table(estat.dezenas())

            st.subheader("📅 Frequência dos Meses da Sorte")
            st.table(estat.meses())

        # ---------- ABA CONFERIR ----------
        with abas[2]:
            if st.button("✅ Conferir Cartões"):
                avaliador = AvaliadorService()
                aprendizado = AprendizadoService()

                cartoes = st.session_state.get("cartoes", [])
                estrategia_nome = st.session_state.get("estrategia", "Desconhecida")

                resultados = avaliador.avaliar(cartoes)
                score = avaliador.score_medio(resultados)

                aprendizado.salvar(estrategia_nome, score)

                st.metric("🎯 Score médio", score)

                for r in resultados:
                    st.write(r)


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    StreamlitApp().run()
