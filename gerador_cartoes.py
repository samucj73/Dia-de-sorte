import random
from collections import Counter

def calcular_frequencias(sorteios):
    todas_dezenas = []
    todos_meses = []
    for s in sorteios:
        todas_dezenas.extend(s['dezenas'])
        todos_meses.append(s['mesSorte'])
    return Counter(todas_dezenas), Counter(todos_meses)

def simular_acertos(cartao, sorteios, concursos_simulados=100):
    acertos = []
    for s in sorteios[:concursos_simulados]:
        dezenas_sorteadas = set(s['dezenas'])
        acertos.append(len(set(cartao['dezenas']) & dezenas_sorteadas))
    return sum(acertos) / len(acertos) if acertos else 0

def gerar_cartao(dezenas_disponiveis, meses_validos):
    dezenas = random.sample(dezenas_disponiveis, 7)
    mes = random.choice(meses_validos)
    return {"dezenas": sorted(dezenas), "mesSorte": mes}

def gerar_cartoes_otimizados_adaptativo(qtd, sorteios, desempenho_minimo=4.5, max_tentativas=30000):
    freq_dezenas, freq_meses = calcular_frequencias(sorteios)
    meses_validos = [m for m, _ in freq_meses.most_common()]
    
    cartoes_gerados = []
    tentativas = 0
    dezenas_base = 20

    while len(cartoes_gerados) < qtd and tentativas < max_tentativas:
        dezenas_validas = [d for d, _ in freq_dezenas.most_common(dezenas_base)]

        if len(dezenas_validas) < 7:
            break  # não é possível montar um cartão

        cartao = gerar_cartao(dezenas_validas, meses_validos)
        media_acertos = simular_acertos(cartao, sorteios)

        if media_acertos >= desempenho_minimo and cartao not in cartoes_gerados:
            cartoes_gerados.append(cartao)

        tentativas += 1

        # Se muitas tentativas sem sucesso, expande universo de dezenas
        if tentativas % 3000 == 0 and dezenas_base < 31:
            dezenas_base += 2  # aumenta progressivamente

    return cartoes_gerados
