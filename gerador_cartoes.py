import random

def gerar_cartoes_otimizados(qtd, concursos, tentativas=10000, desempenho_minimo=5.0):
    todos_cartoes = []
    dezenas_anteriores = [set(c["dezenas"]) for c in concursos]
    meses_anteriores = [c.get("mesSorte", "") for c in concursos]
    dezenas_validas = [str(i).zfill(2) for i in range(1, 32)]
    meses_validos = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    def simular_acertos(cartao_dezenas, mes_sorte):
        acertos = []
        for i, c in enumerate(concursos[:20]):  # simula nos últimos 20 concursos
            dezenas_sorteadas = set(c["dezenas"])
            acerto = len(dezenas_sorteadas.intersection(cartao_dezenas))
            if mes_sorte == c.get("mesSorte", ""):
                acerto += 1  # bônus se acertar o mês
            acertos.append(acerto)
        return sum(acertos) / len(acertos)

    # Gerar muitos cartões e filtrar os melhores
    for _ in range(tentativas):
        dezenas = sorted(random.sample(dezenas_validas, 7))
        mes_sorte = random.choice(meses_validos)
        desempenho = simular_acertos(set(dezenas), mes_sorte)
        if desempenho >= desempenho_minimo:
            todos_cartoes.append({
                "dezenas": dezenas,
                "mesSorte": mes_sorte,
                "desempenho": desempenho
            })

    if not todos_cartoes:
        return []

    # Ordena os cartões por desempenho e retorna os melhores
    todos_cartoes.sort(key=lambda x: x["desempenho"], reverse=True)
    return todos_cartoes[:qtd]
