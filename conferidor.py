from diadesorte_stats import carregar_sorteios

def conferir_cartoes(cartoes, concurso=None):
    sorteios = carregar_sorteios()

    # Se nenhum concurso for passado, usa o último
    concurso_ref = sorteios[0] if concurso is None else next((c for c in sorteios if c["concurso"] == concurso), None)

    if not concurso_ref:
        print("Concurso de referência não encontrado.")
        return []

    dezenas_sorteadas = set(map(int, concurso_ref["dezenas"]))
    mes_sorteado = concurso_ref.get("mesSorte", "")  # Corrigido o nome da chave

    resultados = []
    for cartao in cartoes:
        dezenas_cartao = set(cartao["dezenas"])
        acertos = len(dezenas_cartao.intersection(dezenas_sorteadas))
        mes_certo = cartao.get("mesSorte", "") == mes_sorteado

        faixa = {
            7: "🏆 1º prêmio (7 acertos)",
            6: "🥈 2º prêmio (6 acertos)",
            5: "🥉 3º prêmio (5 acertos)"
        }.get(acertos, "Sem premiação")

        resultados.append({
            "dezenas": sorted(cartao["dezenas"]),
            "mesSorte": cartao.get("mesSorte", ""),
            "acertos": acertos,
            "mes_certo": mes_certo,
            "faixa": faixa
        })

    return resultados

# Exemplo de uso
if __name__ == "__main__":
    from gerador_cartoes import gerar_cartoes_otimizados

    cartoes = gerar_cartoes_otimizados(5)
    resultados = conferir_cartoes(cartoes)

    for i, r in enumerate(resultados, 1):
        print(f"Cartão {i}: {r['dezenas']} | Acertos: {r['acertos']} | Mês certo: {r['mes_certo']} → {r['faixa']}")
