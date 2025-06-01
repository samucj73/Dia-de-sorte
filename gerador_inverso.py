import random
from collections import Counter

def calcular_frequencias_inversas(sorteios):
    todas_dezenas = []
    todos_meses = []
    for s in sorteios:
        todas_dezenas.extend(s['dezenas'])
        todos_meses.append(s['mesSorte'])
    return Counter(todas_dezenas), Counter(todos_meses)

def gerar_cartao_inverso(dezenas_menos_frequentes, meses_menos_frequentes):
    dezenas = random.sample(dezenas_menos_frequentes, 7)
    mes = random.choice(meses_menos_frequentes)
    return {"dezenas": sorted(dezenas), "mesSorte": mes}

def gerar_cartoes_inversos(qtd, sorteios):
    freq_dezenas, freq_meses = calcular_frequencias_inversas(sorteios)
    dezenas_menos_frequentes = [d for d, _ in freq_dezenas.most_common()][-20:]  # 20 menos frequentes
    meses_menos_frequentes = [m for m, _ in freq_meses.most_common()][-6:]       # 6 menos frequentes

    cartoes = []
    tentativas = 0
    while len(cartoes) < qtd and tentativas < 5000:
        tentativas += 1
        cartao = gerar_cartao_inverso(dezenas_menos_frequentes, meses_menos_frequentes)
        if cartao not in cartoes:
            cartoes.append(cartao)
    return cartoes
