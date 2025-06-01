import streamlit as st
from gerador_cartoes import gerar_cartoes_otimizados_adaptativo as gerar_cartoes_otimizados
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

# ---------- SLIDER DE CONCURSOS ----------
qtd_concursos = st.slider("Quantos concursos deseja carregar para análise?", min_value=30, max_value=300, value=100, step=10)

# ---------- CACHE DE SORTEIOS ----------
@st.cache_data(ttl=3600)
def get_sorteios(n):
    sorteios = baixar_ultimos_sorteios(n)
    if not sorteios:
        st.error("Não foi possível carregar os sorteios. Tente novamente mais tarde.")
    return sorteios

sorteios = get_sorteios(qtd_concursos)

# ---------- EXIBIR ÚLTIMO CONCURSO ----------
if sorteios:
    ultimo = sorteios[0]
    st.markdown("### Último Concurso")
    st.markdown(f"**Concurso:** {ultimo['concurso']}")
    st.markdown(f"**Data:** {ultimo['data']}")
    st.markdown(f"**Dezenas sorteadas:** {', '.join(ultimo['dezenas'])}")
    st.markdown(f"**Mês da Sorte:** {ultimo.get('mesSorte', 'Desconhecido')}")

st.markdown("---")

# ---------- ABAS ----------
abas = st.tabs(["🎯 Gerar Cartões", "📊 Análises", "✅ Conferência"])

# ---------- ABA 1: GERADOR DE CARTÕES ----------
with abas[0]:
    st.markdown("### 🎯 Geração de Cartões Otimizados")
    qtd = st.number_input("Quantos cartões deseja gerar?", min_value=1, max_value=200, value=5)

    desempenho_minimo = st.slider("Desempenho mínimo (média de acertos nos últimos concursos)", 3.0, 6.0, 4.5, 0.1)

    if st.button("🔄 Gerar Cartões"):
        if sorteios:
            cartoes = gerar_cartoes_otimizados(qtd, sorteios, desempenho_minimo=desempenho_minimo, max_tentativas=30000)
            if cartoes:
                st.success(f"{len(cartoes)} cartões gerados com sucesso!")
                for i, c in enumerate(cartoes, 1):
                    st.write(f"**Cartão {i}**: {c['dezenas']} | Mês da Sorte: {c['mesSorte']}")
                st.session_state["cartoes_gerados"] = cartoes
            else:
                st.warning("⚠️ Nenhum cartão gerado com os critérios definidos. Tente reduzir o desempenho mínimo ou aumentar a quantidade de concursos analisados.")
        else:
            st.error("Sem dados de sorteios para gerar cartões.")

# ---------- ABA 2: ANÁLISES ESTATÍSTICAS ----------
with abas[1]:
    st.markdown("### 📊 Análises dos Últimos Concursos")
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
    else:
        st.warning("Sem dados suficientes para análises estatísticas.")

# ---------- ABA 3: CONFERÊNCIA ----------
with abas[2]:
    st.markdown("### ✅ Conferência de Cartões")
    st.write("Clique no botão abaixo para conferir os cartões gerados com o último concurso disponível.")
    if st.button("Conferir Agora"):
        if "cartoes_gerados" in st.session_state and st.session_state["cartoes_gerados"]:
            cartoes = st.session_state["cartoes_gerados"]
            resultados = conferir_cartoes(cartoes)

            for i, r in enumerate(resultados, 1):
                st.markdown(f"""
                ---
                ### 🃏 Cartão {i}
                - **Dezenas:** `{r['dezenas']}`
                - **Mês da Sorte:** `{r.get('mesSorte', 'Desconhecido')}`
                - 🎯 **Acertos:** `{r['acertos']}`
                - 📅 **Mês certo:** {"✅ Sim" if r['mes_certo'] else "❌ Não"}
                - 🏅 **Faixa:** `{r['faixa']}`
                """)
        else:
            st.warning("Nenhum cartão gerado encontrado. Vá até a aba '🎯 Gerar Cartões' e gere seus jogos antes de conferir.")

# ---------- RODAPÉ ----------
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 14px;'>© 2025 - Desenvolvido com 💡 para a Dia de Sorte Inteligente</p>", unsafe_allow_html=True)
