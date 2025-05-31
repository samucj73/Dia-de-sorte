import streamlit as st
from gerador_cartoes import gerar_cartoes_otimizados
from diadesorte_stats import (
    frequencia_dezenas, frequencia_meses, pares_impares,
    soma_dezenas, sequencias_consecutivas, repeticao_entre_concursos
)
from conferidor import conferir_cartoes
from diadesorte_api import baixar_ultimos_sorteios

# ---------- CONFIGURAÇÃO INICIAL ----------
st.set_page_config(page_title="Dia de Sorte Inteligente", layout="wide")
st.markdown("<h1 style='text-align: center;'>💡 Dia de Sorte Inteligente</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------- CACHE DE SORTEIOS ----------
@st.cache_data(ttl=3600)
def get_sorteios():
    sorteios = baixar_ultimos_sorteios(30)
    if not sorteios:
        st.error("Não foi possível carregar os últimos sorteios. Tente recarregar mais tarde.")
    return sorteios

sorteios = get_sorteios()

# ---------- EXIBIR ÚLTIMO CONCURSO ----------
if sorteios:
    ultimo = sorteios[0]
    dezenas = ", ".join(ultimo.get("dezenas", []))
    concurso = ultimo.get("concurso", "N/A")
    data = ultimo.get("data", "Data não disponível")
    mes = ultimo.get("mes_sorte", "Desconhecido")

    st.markdown("### 🗓️ Último Concurso")
    st.info(
        f"**Concurso {concurso}** — {data}\n\n"
        f"**Dezenas Sorteadas:** {dezenas}\n\n"
        f"**Mês da Sorte:** {mes}"
    )

# ---------- ABAS ----------
abas = st.tabs(["🎯 Gerar Cartões", "📊 Análises", "✅ Conferência"])

# ---------- ABA 1: GERADOR DE CARTÕES ----------
with abas[0]:
    st.markdown("### 🎯 Geração de Cartões Otimizados")
    qtd = st.number_input("Quantos cartões deseja gerar?", min_value=1, max_value=20, value=5)
    
    if st.button("🔄 Gerar Cartões"):
        if sorteios:
            cartoes = gerar_cartoes_otimizados(qtd, sorteios)
            st.success(f"{len(cartoes)} cartões gerados com sucesso!")
            for i, c in enumerate(cartoes, 1):
                dezenas = c.get("dezenas", [])
                mes = c.get("mes_da_sorte", "Desconhecido")
                st.write(f"**Cartão {i}**: {dezenas} | Mês da Sorte: {mes}")
            st.session_state["cartoes_gerados"] = cartoes
        else:
            st.error("Sem dados de sorteios para gerar cartões.")

# ---------- ABA 2: ANÁLISES ESTATÍSTICAS ----------
with abas[1]:
    st.markdown("### 📊 Análises dos Últimos 30 Concursos")
    if sorteios:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 Dezenas Mais Frequentes")
            freq = frequencia_dezenas(sorteios)
            st.table(freq)

        with col2:
            st.subheader("📅 Meses da Sorte Mais Frequentes")
            freq_meses = frequencia_meses(sorteios)
            st.table(freq_meses)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("➗ Pares e Ímpares")
            distrib = pares_impares(sorteios)
            for i, d in enumerate(distrib, 1):
                pares = d.get("pares", 0)
                impares = d.get("ímpares", 0)
                st.write(f"Concurso {i}: {pares} pares, {impares} ímpares")

        with col4:
            st.subheader("🧮 Soma das Dezenas")
            soma = soma_dezenas(sorteios)
            st.line_chart(soma)

        st.subheader("📶 Sequências Consecutivas")
        seqs = sequencias_consecutivas(sorteios)
        for i, s in enumerate(seqs, 1):
            if s:
                st.write(f"Concurso {i}: {s}")

        st.subheader("🔁 Repetições em Relação ao Concurso Anterior")
        reps = repeticao_entre_concursos(sorteios)
        st.bar_chart(reps)
    else:
        st.warning("Sem dados suficientes para análises estatísticas.")

# ---------- ABA 3: CONFERÊNCIA ----------
with abas[2]:
    st.markdown("### ✅ Conferência de Cartões")
    
    if "cartoes_gerados" in st.session_state and sorteios:
        cartoes = st.session_state["cartoes_gerados"]
        st.info("Conferindo os cartões gerados com o último concurso disponível.")
        ultimo_concurso = sorteios[0]
        resultados = conferir_cartoes(cartoes, ultimo_concurso)
        for i, r in enumerate(resultados, 1):
            cor = "🟢" if r.get("acertos", 0) >= 5 else "🔴"
            dezenas = r.get("dezenas", [])
            acertos = r.get("acertos", 0)
            mes_cartao = r.get("mes_da_sorte", "Indefinido")
            mes_certo = r.get("mes_certo", "Indefinido")
            faixa = r.get("faixa", "Sem prêmio")
            st.write(
                f"{cor} **Cartão {i}**: {dezenas} | Acertos: {acertos} | "
                f"Mês da Sorte: {mes_cartao} | Mês correto: {mes_certo} → **{faixa}**"
            )
    else:
        st.warning("Gere os cartões na aba '🎯 Gerar Cartões' antes de realizar a conferência.")

# ---------- RODAPÉ ----------
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 14px;'>© 2025 - Desenvolvido com 💡 para a Dia de Sorte Inteligente</p>", unsafe_allow_html=True)
