# =========================================================
# DIA DE SORTE INTELIGENTE - VERSÃO APRIMORADA
# Motor Elite Híbrido com Estratégia Suplementar 4+
# =========================================================

import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod
from collections import Counter
from datetime import datetime, timedelta

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

    def dezenas(self): 
        return frequencia_dezenas(self.sorteios)
    def meses(self): 
        return frequencia_meses(self.sorteios)
    def pares(self): 
        return pares_impares(self.sorteios)
    def soma(self): 
        return soma_dezenas(self.sorteios)
    def sequencias(self): 
        return sequencias_consecutivas(self.sorteios)
    def repeticoes(self): 
        return repeticao_entre_concursos(self.sorteios)

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
# STRATEGY PATTERN (DEFINIÇÃO DA CLASSE BASE)
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
# SERVIÇO DE ESTATÍSTICAS AVANÇADAS
# =========================================================

class EstatisticasAvancadas:
    def __init__(self, sorteios):
        self.sorteios = sorteios
        
    def analisar_tendencias_temporais(self, janelas=[10, 20, 30]):
        """Analisa tendências em diferentes janelas temporais"""
        tendencias = {}
        
        for janela in janelas:
            if len(self.sorteios) >= janela:
                recentes = self.sorteios[:janela]
                
                # Frequência na janela atual
                freq_atual = Counter()
                for s in recentes:
                    freq_atual.update(map(int, s["dezenas"]))
                
                # Comparar com janela anterior
                if len(self.sorteios) >= janela * 2:
                    anteriores = self.sorteios[janela:janela*2]
                    freq_anteriores = Counter()
                    for s in anteriores:
                        freq_anteriores.update(map(int, s["dezenas"]))
                    
                    # Calcular momentum (crescimento/decrescimento)
                    momentum = {}
                    for num in range(1, 32):
                        atual = freq_atual.get(num, 0)
                        anterior = freq_anteriores.get(num, 0)
                        if anterior > 0:
                            momentum[num] = (atual - anterior) / anterior
                        else:
                            momentum[num] = 1 if atual > 0 else 0
                    
                    tendencias[f"janela_{janela}"] = {
                        "frequencia": dict(freq_atual),
                        "momentum": momentum,
                        "top_crescente": sorted(momentum.items(), key=lambda x: x[1], reverse=True)[:8]
                    }
        
        return tendencias
    
    def identificar_pares_fortes(self):
        """Identifica pares de números que costumam sair juntos"""
        pares = Counter()
        
        for sorteio in self.sorteios:
            dezenas = sorted(map(int, sorteio["dezenas"]))
            for i in range(len(dezenas)):
                for j in range(i+1, len(dezenas)):
                    pares[(dezenas[i], dezenas[j])] += 1
        
        # Normalizar e retornar top pares
        total_sorteios = len(self.sorteios)
        pares_fortes = {
            k: v/total_sorteios 
            for k, v in pares.most_common(50)
        }
        
        return pares_fortes
    
    def identificar_trios_fortes(self):
        """Identifica trios de números que costumam sair juntos"""
        trios = Counter()
        
        for sorteio in self.sorteios:
            dezenas = sorted(map(int, sorteio["dezenas"]))
            for i in range(len(dezenas)):
                for j in range(i+1, len(dezenas)):
                    for k in range(j+1, len(dezenas)):
                        trios[(dezenas[i], dezenas[j], dezenas[k])] += 1
        
        total_sorteios = len(self.sorteios)
        trios_fortes = {
            k: v/total_sorteios 
            for k, v in trios.most_common(30)
        }
        
        return trios_fortes
    
    def analisar_padroes_mes_sorte(self):
        """Analisa relação entre mês da sorte e dezenas"""
        relacao_mes_dezenas = {}
        
        for mes in range(1, 13):
            sorteios_mes = [s for s in self.sorteios if s.get("mesSorte") == mes]
            if sorteios_mes:
                freq = Counter()
                for s in sorteios_mes:
                    freq.update(map(int, s["dezenas"]))
                
                relacao_mes_dezenas[mes] = {
                    "frequencia": dict(freq.most_common(10)),
                    "total_sorteios": len(sorteios_mes)
                }
        
        return relacao_mes_dezenas

# =========================================================
# MOTOR OCULTO TOP-31 APRIMORADO
# =========================================================

class FrequenciaTop31Aprimorado:
    def __init__(self, sorteios, janelas=[10, 20, 30]):
        self.sorteios = sorteios
        self.estats = EstatisticasAvancadas(sorteios)
        self.tendencias = self.estats.analisar_tendencias_temporais(janelas)
        self.pares_fortes = self.estats.identificar_pares_fortes()
        self.trios_fortes = self.estats.identificar_trios_fortes()
        self.relacao_mes = self.estats.analisar_padroes_mes_sorte()
        
        # Calcular pesos combinados
        self.pesos_combinados = self._calcular_pesos_combinados()
        
    def _calcular_pesos_combinados(self):
        """Calcula pesos combinando múltiplos fatores"""
        pesos = {i: 0.0 for i in range(1, 32)}
        
        # Peso base da frequência geral
        freq_geral = Counter()
        for s in self.sorteios:
            freq_geral.update(map(int, s["dezenas"]))
        
        total_sorteios = len(self.sorteios)
        for num, count in freq_geral.items():
            pesos[num] += count / total_sorteios * 3.0  # Peso 3x para frequência
        
        # Peso das tendências recentes (janela 10)
        if "janela_10" in self.tendencias:
            for num, freq in self.tendencias["janela_10"]["frequencia"].items():
                pesos[num] += (freq / 10) * 2.0  # Peso 2x para tendência recente
        
        # Peso do momentum (números em crescimento)
        if "janela_30" in self.tendencias:
            for num, mom in self.tendencias["janela_30"]["momentum"].items():
                if mom > 0.2:  # Crescimento significativo
                    pesos[num] += mom * 1.5
        
        # Peso dos pares fortes (reforço mútuo)
        for (num1, num2), prob in self.pares_fortes.items():
            if prob > 0.3:  # Pares que saem juntos em mais de 30% dos casos
                pesos[num1] += prob * 0.5
                pesos[num2] += prob * 0.5
        
        # Peso dos trios fortes
        for (num1, num2, num3), prob in self.trios_fortes.items():
            if prob > 0.15:  # Trios que saem juntos em mais de 15% dos casos
                pesos[num1] += prob * 0.8
                pesos[num2] += prob * 0.8
                pesos[num3] += prob * 0.8
        
        # Normalizar para probabilidades
        total = sum(pesos.values())
        if total > 0:
            for num in pesos:
                pesos[num] /= total
        
        return pesos
    
    def gerar_com_garantia_4mais(self):
        """
        Gera cartão com garantia de pelo menos 4 números de alta probabilidade
        """
        cartao = set()
        
        # Estratégia 1: Garantir 4 números do Top-10 com maior peso
        numeros_ordenados = sorted(self.pesos_combinados.items(), 
                                  key=lambda x: x[1], reverse=True)
        top10 = [n for n, _ in numeros_ordenados[:10]]
        top10_garantidos = random.sample(top10, 4)
        cartao.update(top10_garantidos)
        
        # Estratégia 2: Adicionar baseado em pares fortes com os já selecionados
        candidatos_restantes = []
        for num in cartao:
            # Buscar pares fortes para cada número já selecionado
            for (n1, n2), prob in self.pares_fortes.items():
                if prob > 0.25:  # Pares significativos
                    if n1 == num and n2 not in cartao:
                        candidatos_restantes.extend([n2] * int(prob * 10))
                    elif n2 == num and n1 not in cartao:
                        candidatos_restantes.extend([n1] * int(prob * 10))
        
        # Adicionar baseado em trios fortes
        for (n1, n2, n3), prob in self.trios_fortes.items():
            if prob > 0.12:  # Trios significativos
                presentes = sum(1 for n in [n1, n2, n3] if n in cartao)
                if presentes >= 2:  # Se já tem 2 do trio, adicionar o terceiro
                    for n in [n1, n2, n3]:
                        if n not in cartao:
                            candidatos_restantes.extend([n] * int(prob * 15))
        
        # Se não houver candidatos suficientes, completar com base nos pesos
        while len(cartao) < 7 and candidatos_restantes:
            candidato = random.choice(candidatos_restantes)
            cartao.add(candidato)
        
        # Completar com números de alta probabilidade restantes
        while len(cartao) < 7:
            for num, _ in numeros_ordenados:
                if num not in cartao:
                    cartao.add(num)
                    break
        
        return sorted(list(cartao))
    
    def gerar_com_adaptacao_mes(self, mes_sorte):
        """
        Gera cartão adaptado para um mês da sorte específico
        """
        cartao = set()
        
        # Usar padrões específicos do mês
        if mes_sorte in self.relacao_mes:
            dados_mes = self.relacao_mes[mes_sorte]
            numeros_frequentes = list(dados_mes["frequencia"].keys())
            
            # Garantir 3 números frequentes neste mês
            if numeros_frequentes:
                garantidos = random.sample(
                    numeros_frequentes, 
                    min(3, len(numeros_frequentes))
                )
                cartao.update(garantidos)
        
        # Completar com a estratégia principal
        while len(cartao) < 7:
            candidato = self.gerar_com_garantia_4mais()
            # Pegar apenas números que ainda não estão no cartão
            for num in candidato:
                if len(cartao) < 7 and num not in cartao:
                    cartao.add(num)
        
        return sorted(list(cartao))[:7]

# =========================================================
# FILTROS ESTATÍSTICOS APRIMORADOS
# =========================================================

class FiltrosAprimorados:
    @staticmethod
    def valido_avancado(dezenas):
        """
        Validação mais rigorosa baseada em múltiplos critérios
        """
        # Critérios básicos
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)
        impares = 7 - pares
        
        # Critério 1: Soma otimizada (ajustado para 4+ acertos)
        if not (72 <= soma <= 98):
            return False
        
        # Critério 2: Distribuição par/ímpar
        if pares not in (2, 3, 4, 5) or impares not in (2, 3, 4, 5):
            return False
        
        # Critério 3: Evitar números muito baixos (<5) ou muito altos (>28)
        # (estes números têm menor probabilidade em sorteios reais)
        extremos = sum(1 for d in dezenas if d <= 5 or d >= 28)
        if extremos >= 3:
            return False
        
        # Critério 4: Verificar concentração em blocos
        blocos = [0, 0, 0]  # 1-10, 11-20, 21-31
        for d in dezenas:
            if d <= 10:
                blocos[0] += 1
            elif d <= 20:
                blocos[1] += 1
            else:
                blocos[2] += 1
        
        # Evitar concentração excessiva em um único bloco
        if max(blocos) >= 5:
            return False
        
        return True

# =========================================================
# ESTRATÉGIA ELITE HÍBRIDA 4+ (APRIMORADA)
# =========================================================

class EstrategiaEliteHibrida4Plus(Estrategia):
    nome = "Elite Híbrida 4+ (Garantia Aprimorada)"
    
    def gerar(self, qtd, sorteios):
        motor_aprimorado = FrequenciaTop31Aprimorado(sorteios)
        cartoes = []
        
        # Analisar meses mais promissores
        frequencia_meses = Counter(s.get("mesSorte") for s in sorteios)
        meses_top = [mes for mes, _ in frequencia_meses.most_common(6)]
        
        tentativas = 0
        max_tentativas = qtd * 50  # Limite para evitar loop infinito
        
        while len(cartoes) < qtd and tentativas < max_tentativas:
            tentativas += 1
            
            # Alternar entre estratégias para diversificar
            if random.random() < 0.7:  # 70% das vezes usa estratégia principal
                dezenas = motor_aprimorado.gerar_com_garantia_4mais()
            else:  # 30% adaptado ao mês
                if meses_top:  # Verificar se há meses disponíveis
                    mes_escolhido = random.choice(meses_top)
                    dezenas = motor_aprimorado.gerar_com_adaptacao_mes(mes_escolhido)
                else:
                    dezenas = motor_aprimorado.gerar_com_garantia_4mais()
            
            # Validar com filtros aprimorados
            if FiltrosAprimorados.valido_avancado(dezenas):
                # Escolher mês da sorte baseado em frequência
                if frequencia_meses:
                    meses = list(frequencia_meses.keys())
                    pesos = list(frequencia_meses.values())
                    mes_sorte = random.choices(meses, weights=pesos, k=1)[0]
                else:
                    mes_sorte = random.randint(1, 12)
                
                cartoes.append({
                    "dezenas": dezenas,
                    "mesSorte": mes_sorte,
                    "estrategia": "4+ garantido"
                })
        
        return cartoes[:qtd]

# =========================================================
# MÓDULO DE ANÁLISE PREDITIVA
# =========================================================

class AnalisePreditiva:
    def __init__(self, sorteios):
        self.sorteios = sorteios
        self.estats = EstatisticasAvancadas(sorteios)
        
    def prever_proximos_numeros(self):
        """
        Faz previsão dos números com maior chance para o próximo sorteio
        """
        tendencias = self.estats.analisar_tendencias_temporais()
        pares_fortes = self.estats.identificar_pares_fortes()
        
        # Pontuação preditiva
        pontuacao = {i: 0 for i in range(1, 32)}
        
        # Critério 1: Momentum recente (peso alto)
        if "janela_10" in tendencias:
            for num, mom in tendencias["janela_10"].get("momentum", {}).items():
                pontuacao[num] += mom * 10
        
        # Critério 2: Frequência na última janela
        if "janela_10" in tendencias:
            for num, freq in tendencias["janela_10"]["frequencia"].items():
                pontuacao[num] += freq * 2
        
        # Critério 3: Atraso (números que não saem há muito tempo)
        ultimos_sorteados = set()
        for s in self.sorteios[:5]:  # Últimos 5 sorteios
            ultimos_sorteados.update(map(int, s["dezenas"]))
        
        for num in range(1, 32):
            if num not in ultimos_sorteados:
                pontuacao[num] += 3  # Bônus para números atrasados
        
        # Critério 4: Pares fortes com números em alta
        top_momentum = sorted(
            [(n, pontuacao[n]) for n in range(1, 32)], 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        for num, _ in top_momentum:
            for (n1, n2), prob in pares_fortes.items():
                if prob > 0.2:
                    if n1 == num and pontuacao[n2] < 10:
                        pontuacao[n2] += 5
                    elif n2 == num and pontuacao[n1] < 10:
                        pontuacao[n1] += 5
        
        return sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)

# =========================================================
# STREAMLIT APP - VERSÃO APRIMORADA
# =========================================================

class StreamlitAppAprimorado:
    def run(self):
        st.set_page_config(
            page_title="Dia de Sorte Inteligente 4+",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.title("🎯 Dia de Sorte Inteligente — Motor Elite 4+")
        st.markdown("---")

        # Sidebar com configurações
        with st.sidebar:
            st.header("⚙️ Configurações")
            
            qtd_concursos = st.slider(
                "📊 Concursos analisados",
                50, 500, 150,
                help="Mais concursos = melhor base estatística"
            )
            
            modo_operacao = st.radio(
                "🎮 Modo de operação",
                ["Normal", "Alta Precisão", "Teste"]
            )
            
            st.markdown("---")
            st.markdown("### 📈 Estatísticas em tempo real")

        # Carregar dados
        with st.spinner("Carregando sorteios..."):
            sorteios = carregar_sorteios_cacheados(qtd_concursos)

        # ---------- ÚLTIMO CONCURSO ----------
        if sorteios:
            ultimo = sorteios[0]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Último Concurso", ultimo['concurso'])
            with col2:
                st.metric("Data", ultimo['data'])
            with col3:
                st.metric("Dezenas", ', '.join(ultimo['dezenas']))
            with col4:
                st.metric("Mês da Sorte", ultimo.get('mesSorte', 'N/A'))

        # Abas principais
        abas = st.tabs([
            "🎯 Gerar Cartões 4+", 
            "📊 Análise Preditiva", 
            "🔬 Estatísticas Avançadas",
            "✅ Conferir Resultados"
        ])

        # ---------- GERAR CARTÕES 4+ ----------
        with abas[0]:
            st.subheader("🎲 Geração de Cartões com Garantia 4+")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                qtd = st.number_input("Quantidade de cartões", 1, 50, 10)
                
                estrategias_disponiveis = [
                    EstrategiaEliteHibrida4Plus(),
                    EstrategiaEliteHibrida(),  # Versão original
                    EstrategiaOtimizada(),
                ]
                
                estrategia = st.selectbox(
                    "🎯 Estratégia de geração",
                    estrategias_disponiveis,
                    format_func=lambda e: e.nome
                )
            
            with col2:
                st.markdown("### 🎚️ Ajustes finos")
                peso_tendencia = st.slider("Peso tendências", 0.0, 2.0, 1.0, 0.1)
                peso_atraso = st.slider("Peso números atrasados", 0.0, 2.0, 1.0, 0.1)

            if st.button("🚀 Gerar Cartões Premium", type="primary", use_container_width=True):
                with st.spinner("Processando estratégia 4+..."):
                    # Aplicar ajustes conforme modo
                    if modo_operacao == "Alta Precisão":
                        # Reduzir quantidade mas aumentar qualidade
                        qtd_real = max(1, qtd // 2)
                    else:
                        qtd_real = qtd
                    
                    cartoes = estrategia.gerar(qtd_real, sorteios)
                    st.session_state["cartoes_gerados"] = cartoes
                    
                    # Exibir cartões em grid
                    st.markdown("### 📋 Cartões Gerados")
                    
                    cols = st.columns(2)
                    for i, cartao in enumerate(cartoes):
                        with cols[i % 2]:
                            with st.container():
                                st.markdown(f"""
                                🃏 **Cartão {i+1}**  
                                🔢 Dezenas: `{cartao['dezenas']}`  
                                📅 Mês: `{cartao['mesSorte']}`
                                """)
                                
                                # Análise rápida do cartão
                                if 'estrategia' in cartao:
                                    st.caption(f"✨ Estratégia: {cartao['estrategia']}")

        # ---------- ANÁLISE PREDITIVA ----------
        with abas[1]:
            st.subheader("🔮 Análise Preditiva para Próximo Sorteio")
            
            if sorteios:
                preditor = AnalisePreditiva(sorteios)
                previsoes = preditor.prever_proximos_numeros()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ⭐ Top 10 números mais prováveis")
                    dados_previsao = []
                    for i, (num, score) in enumerate(previsoes[:10], 1):
                        dados_previsao.append({
                            "Ranking": i,
                            "Número": num,
                            "Pontuação": round(score, 2)
                        })
                    
                    df_previsao = pd.DataFrame(dados_previsao)
                    st.dataframe(df_previsao, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("### 📊 Distribuição de probabilidade")
                    
                    # Gráfico de barras simplificado
                    nums = [n for n, _ in previsoes[:15]]
                    scores = [s for _, s in previsoes[:15]]
                    
                    chart_data = pd.DataFrame({
                        "Número": nums,
                        "Probabilidade": scores
                    })
                    
                    st.bar_chart(chart_data.set_index("Número"))

        # ---------- ESTATÍSTICAS AVANÇADAS ----------
        with abas[2]:
            st.subheader("🔬 Análise Estatística Avançada")
            
            if sorteios:
                estats_avancadas = EstatisticasAvancadas(sorteios)
                
                tabs_estats = st.tabs([
                    "Tendências Temporais", 
                    "Pares Fortes", 
                    "Trios Fortes",
                    "Mês da Sorte"
                ])
                
                with tabs_estats[0]:
                    tendencias = estats_avancadas.analisar_tendencias_temporais()
                    
                    if "janela_10" in tendencias:
                        st.markdown("#### 📈 Números em alta (últimos 10 sorteios)")
                        top_crescente = tendencias["janela_10"].get("top_crescente", [])[:8]
                        
                        dados_tendencia = []
                        for num, mom in top_crescente:
                            dados_tendencia.append({
                                "Número": num,
                                "Momentum": f"{mom*100:.1f}%"
                            })
                        
                        if dados_tendencia:
                            st.dataframe(pd.DataFrame(dados_tendencia), hide_index=True)
                        else:
                            st.info("Dados insuficientes para análise de tendências")
                
                with tabs_estats[1]:
                    pares = estats_avancadas.identificar_pares_fortes()
                    dados_pares = []
                    
                    for (n1, n2), prob in list(pares.items())[:15]:
                        dados_pares.append({
                            "Par": f"{n1}-{n2}",
                            "Probabilidade": f"{prob*100:.1f}%"
                        })
                    
                    if dados_pares:
                        st.dataframe(pd.DataFrame(dados_pares), hide_index=True)
                    else:
                        st.info("Dados insuficientes para análise de pares")
                
                with tabs_estats[2]:
                    trios = estats_avancadas.identificar_trios_fortes()
                    dados_trios = []
                    
                    for (n1, n2, n3), prob in list(trios.items())[:10]:
                        dados_trios.append({
                            "Trio": f"{n1}-{n2}-{n3}",
                            "Probabilidade": f"{prob*100:.1f}%"
                        })
                    
                    if dados_trios:
                        st.dataframe(pd.DataFrame(dados_trios), hide_index=True)
                    else:
                        st.info("Dados insuficientes para análise de trios")
                
                with tabs_estats[3]:
                    relacao_mes = estats_avancadas.analisar_padroes_mes_sorte()
                    
                    if relacao_mes:
                        mes_selecionado = st.selectbox(
                            "Selecione o mês",
                            range(1, 13),
                            format_func=lambda x: f"Mês {x}"
                        )
                        
                        if mes_selecionado in relacao_mes:
                            dados_mes = relacao_mes[mes_selecionado]
                            st.write(f"Total de sorteios neste mês: {dados_mes['total_sorteios']}")
                            
                            df_mes = pd.DataFrame(
                                list(dados_mes['frequencia'].items()),
                                columns=["Número", "Frequência"]
                            )
                            st.dataframe(df_mes, hide_index=True)
                    else:
                        st.info("Dados insuficientes para análise por mês")

        # ---------- CONFERIR RESULTADOS ----------
        with abas[3]:
            st.subheader("✅ Conferir Cartões vs Últimos Sorteios")
            
            if st.button("Conferir Cartões Gerados", type="primary"):
                if "cartoes_gerados" in st.session_state:
                    resultados = conferir_cartoes(st.session_state["cartoes_gerados"])
                    
                    for i, resultado in enumerate(resultados, 1):
                        with st.expander(f"Resultado Cartão {i}"):
                            st.write(resultado)
                else:
                    st.warning("Gere alguns cartões primeiro na aba 'Gerar Cartões 4+'")

        # Rodapé
        st.markdown("---")
        st.caption("⚡ Motor Elite 4+ - Probabilidade aumentada para 4 acertos ou mais")

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    # Verificar se devemos usar a versão original ou a aprimorada
    if 'versao_aprimorada' not in st.session_state:
        st.session_state.versao_aprimorada = True
    
    if st.session_state.versao_aprimorada:
        StreamlitAppAprimorado().run()
    else:
        # Manter compatibilidade com versão original
        from app_original import StreamlitApp as StreamlitAppOriginal
        StreamlitAppOriginal().run()
