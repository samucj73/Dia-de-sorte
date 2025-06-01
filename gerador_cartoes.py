import random
from collections import Counter
from diadesorte_stats import (
    carregar_sorteios, frequencia_dezenas, frequencia_meses,
    soma_dezenas, pares_impares
)

def simular_acertos(cartao, sorteios):
    acertos = []
    for s in sorteios:
        dezenas_sorteadas = set(map(int, s["dezenas"]))
        acerto = len(set(cartao["dezenas"]) & dezenas_sorteadas)
        acertos.append(acerto)
    return sum(acertos) / len(acertos)

def gerar_cartoes_otimizados(qtd=5, sorteios=None):
    if sorteios is None:
        sorteios = carregar_sorteios()
    if not sorteios:
        raise ValueError("Não há sorteios disponíveis.")

    freq_dezenas = frequencia_dezenas(sorteios)
    freq_meses = frequencia_meses(sorteios)
    soma_todas = soma_dezenas(sorteios)
    media_soma = sum(soma_todas) / len(soma_todas)
    min_soma = media_soma - 10
    max_soma = media_soma + 10

    pares_impares_todos = pares_impares(sorteios)
    media_pares = round(sum(p["pares"] for p in pares_impares_todos) / len(pares_impares_todos))

    ultimas_dezenas = list(map(int, sorteios[0]["dezenas"]))
    sorteios_anteriores = sorteios[:20]
    todas_dezenas = list(range(1, 32))
    dezenas_frequentes = sorted(freq_dezenas, key=freq_dezenas.get, reverse=True)[:20]
    meses_frequentes = list(freq_meses.keys())

    cartoes = []
    tentativas = 0
    max_tentativas = 3000

    while len(cartoes) < qtd and tentativas < max_tentativas:
        tentativas += 1
        dezenas = sorted(random.sample(dezenas_frequentes, 5) + random.sample(todas_dezenas, 2))
        if dezenas in [c["dezenas"] for c in sorteios]:  # Evitar repetição de concursos reais
            continue

        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)
        if not (min_soma <= soma <= max_soma):
            continue
        if abs(pares - media_pares) > 2:
            continue
        if len(set(dezenas) & set(ultimas_dezenas)) > 4:
            continue

        consecutivas = sum(1 for i in range(1, 7) if dezenas[i] == dezenas[i - 1] + 1)
        if consecutivas > 2:
            continue

        mes = random.choice(meses_frequentes)
        cartao = {"dezenas": dezenas, "mesSorte": mes}
        media_acertos = simular_acertos(cartao, sorteios_anteriores)

        if media_acertos >= 3:  # mínimo de 3 acertos em média
            cartoes.append(cartao)

    return cartoes
