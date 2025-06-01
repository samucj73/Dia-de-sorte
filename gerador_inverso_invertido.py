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

def distribuir_balanceado(dezenas):
    pares = sum(1 for d in dezenas if d % 2 == 0)
    impares = len(dezenas) - pares
    soma = sum(dezenas)
    consecutivos = sum(1 for i in range(1, len(dezenas)) if dezenas[i] - dezenas[i-1] == 1)

    return (
        2 <= pares <= 5 and
        2 <= impares <= 5 and
        105 <= soma <= 175 and
        consecutivos <= 2
    )

def gerar_cartao_inverso_invertido(dezenas_intermediarias, meses_pouco_frequentes, combinacoes_proibidas):
    tentativas = 0
    while tentativas < 1000:
        dezenas = sorted(random.sample(dezenas_intermediarias, 7))
        combinacao = tuple(dezenas)
        if combinacao in combinacoes_proibidas:
            tentativas += 1
            continue

        if not distribuir_balanceado(dezenas):
            tentativas += 1
            continue

        mes = random.choice(meses_pouco_frequentes)
        return {"dezenas": dezenas, "mesSorte": mes}

    return None  # Falha após 1000 tentativas

def gerar_cartoes_inversos_invertidos(qtd, sorteios):
    freq_dezenas, freq_meses, freq_combinacoes = calcular_frequencias(sorteios)

    # Em vez de pegar as mais ou menos frequentes, pegamos as intermediárias (5ª a 20ª posição)
    dezenas_intermediarias = [d for d, _ in freq_dezenas.most_common()][5:25]
    meses_pouco_frequentes = [m for m, _ in freq_meses.most_common()][-6:]  # Menos sorteados
    combinacoes_proibidas = set([comb for comb, _ in freq_combinacoes.most_common(100)])

    cartoes = []
    tentativas = 0
    while len(cartoes) < qtd and tentativas < 5000:
        cartao = gerar_cartao_inverso_invertido(dezenas_intermediarias, meses_pouco_frequentes, combinacoes_proibidas)
        tentativas += 1
        if cartao and cartao not in cartoes:
            cartoes.append(cartao)

    return cartoes
