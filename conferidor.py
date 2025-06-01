from diadesorte_stats import carregar_sorteios

def conferir_cartoes(cartoes, concurso=None):
    sorteios = carregar_sorteios()

    # Usa o último concurso se nenhum for passado
    concurso_ref = sorteios[0] if concurso is None else next((c for c in sorteios if c["concurso"] == concurso), None)

    if not concurso_ref:
        print("Concurso de referência não encontrado.")
        return []

    dezenas_sorteadas = set(map(int, concurso_ref["dezenas"]))
    mes_sorteado = concurso_ref.get("mesSorte", "")

    resultados = []
    for cartao in cartoes:
        # Garante que as dezenas do cartão são ints
        dezenas_cartao = set(int(d) for d in cartao["dezenas"])
        acertos = len(dezenas_cartao.intersection(dezenas_sorteadas))
        mes_certo = cartao.get("mesSorte", "") == mes_sorteado

        faixa = {
            7: "🏆 1º prêmio (7 acertos)",
            6: "🥈 2º prêmio (6 acertos)",
            5: "🥉 3º prêmio (5 acertos)"
        }.get(acertos, "Sem premiação")

        resultados.append({
            "dezenas": sorted(dezenas_cartao),
            "mesSorte": cartao.get("mesSorte", ""),
            "acertos": acertos,
            "mes_certo": mes_certo,
            "faixa": faixa
        })

    return resultados

# Teste rápido se rodar direto
if __name__ == "__main__":
    from gerador_cartoes import gerar_cartoes_otimizados
    from gerador_inverso import gerar_cartoes_inversos
    from diadesorte_stats import carregar_sorteios

    sorteios = carregar_sorteios()

    print("\n✅ Conferência dos cartões otimizados:")
    cartoes_otimizados = gerar_cartoes_otimizados(qtd=5, sorteios=sorteios)
    resultados_otimizados = conferir_cartoes(cartoes_otimizados)
    for i, r in enumerate(resultados_otimizados, 1):
        print(f"Cartão {i}: {r['dezenas']} | Acertos: {r['acertos']} | Mês certo: {r['mes_certo']} → {r['faixa']}")

    print("\n🌀 Conferência dos cartões inversos:")
    cartoes_inversos = gerar_cartoes_inversos(qtd=5, sorteios=sorteios)
    resultados_inversos = conferir_cartoes(cartoes_inversos)
    for i, r in enumerate(resultados_inversos, 1):
        print(f"Cartão {i}: {r['dezenas']} | Acertos: {r['acertos']} | Mês certo: {r['mes_certo']} → {r['faixa']}")
