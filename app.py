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
    return baixar_ultimos_sorteios()

sorteios = get_sorteios()

# ---------- ABAS ----------
aba = st.tabs(["🎯 Gerar Cartões", "📊 Análises", "✅ Conferência"])

# ---------- ABA 1: GERADOR DE CARTÕES ----------
with aba[0]:
    st.markdown("### 🎯 Geração de Cartões Otimizados")
    qtd = st.number_input("Quantos cartões deseja gerar?", min_value=1, max_value=20, value=5)
    
    if st.button("🔄 Gerar Cartões"):
        cartoes = gerar_cartoes_otimizados(qtd)
        st.success(f"{len(cartoes)} cartões gerados com sucesso!")
        for i, c in enumerate(cartoes, 1):
            st.write(f"**Cartão {i}**: {c['dezenas']} | Mês da Sorte: {c['mes_da_sorte']}")
        st.session_state["cartoes_gerados"] = cartoes

# ---------- ABA 2: ANÁLISES ESTATÍSTICAS ----------
with aba[1]:
    st.markdown("### 📊 Análises dos Últimos 30 Concursos")

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
            st.write(f"Concurso {i}: {d['pares']} pares, {d['ímpares']} ímpares")

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

# ---------- ABA 3: CONFERÊNCIA ----------
with aba[2]:
    st.markdown("### ✅ Conferência de Cartões")
    
    if "cartoes_gerados" in st.session_state:
        cartoes = st.session_state["cartoes_gerados"]
        st.info("Conferindo os cartões gerados com o último concurso disponível.")
        resultados = conferir_cartoes(cartoes, concurso=None)
        for i, r in enumerate(resultados, 1):
            cor = "🟢" if r["acertos"] >= 5 else "🔴"
            st.write(f"{cor} **Cartão {i}**: {r['dezenas']} | Acertos: {r['acertos']} | "
                     f"Mês da Sorte: {r['mes_da_sorte']} | Mês correto: {r['mes_certo']} → **{r['faixa']}**")
    else:
        st.warning("Gere os cartões na aba '🎯 Gerar Cartões' antes de realizar a conferência.")

# ---------- RODAPÉ ----------
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 14px;'>© 2025 - Desenvolvido com 💡 para a Dia de Sorte Inteligente</p>", unsafe_allow_html=True)
