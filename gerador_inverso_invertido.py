import random
from collections import Counter

def calcular_frequencias(sorteios):
    todas_dezenas = []
    todos_meses = []
    combinacoes = []

    for s in sorteios:
        dezenas = list(map(int, s['dezenas']))
        todas_dezenas.extend(dezenas)
        todos_meses.append(s['mesSorte'])
        combinacoes.append(tuple(sorted(dezenas)))

    return Counter(todas_dezenas), Counter(todos_meses), Counter(combinacoes)

def gerar_cartao_inverso_invertido(dezenas_frequentes, meses_frequentes, combinacoes_mais_comuns):
    tentativas = 0
    while tentativas < 1000:
        dezenas = sorted(random.sample(dezenas_frequentes, 7))
        combinacao = tuple(dezenas)
        if combinacao not in combinacoes_mais_comuns:
            mes = random.choice(meses_frequentes)
            return {"dezenas": dezenas, "mesSorte": mes}
        tentativas += 1
    return None  # Falha ao gerar um cartão válido

def gerar_cartoes_inversos_invertidos(qtd, sorteios):
    freq_dezenas, freq_meses, freq_combinacoes = calcular_frequencias(sorteios)
    
    dezenas_frequentes = [d for d, _ in freq_dezenas.most_common(20)]
    meses_frequentes = [m for m, _ in freq_meses.most_common(6)]
    combinacoes_mais_comuns = set([comb for comb, _ in freq_combinacoes.most_common(100)])

    cartoes = []
    tentativas = 0
    while len(cartoes) < qtd and tentativas < 5000:
        tentativas += 1
        cartao = gerar_cartao_inverso_invertido(dezenas_frequentes, meses_frequentes, combinacoes_mais_comuns)
        if cartao and cartao not in cartoes:
            cartoes.append(cartao)
    return cartoes
