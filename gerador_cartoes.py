import random
from collections import Counter

def calcular_frequencias(sorteios):
    todas_dezenas = []
    todos_meses = []
    for s in sorteios:
        todas_dezenas.extend(s['dezenas'])
        todos_meses.append(s['mesSorte'])
    return Counter(todas_dezenas), Counter(todos_meses)

def simular_acertos(cartao, sorteios):
    acertos = []
    for s in sorteios[:20]:  # Simula nos últimos 20 concursos
        dezenas_sorteadas = set(s['dezenas'])
        acertos.append(len(set(cartao['dezenas']) & dezenas_sorteadas))
    return sum(acertos) / len(acertos)

def gerar_cartao(frequencia_dezenas, dezenas_validas, meses_validos):
    # Seleciona 7 dezenas das mais frequentes, equilibrando entre pares/ímpares e distribuição
    dezenas = random.sample(dezenas_validas, 7)
    mes = random.choice(meses_validos)
    return {"dezenas": sorted(dezenas), "mesSorte": mes}

def gerar_cartoes_otimizados(qtd, sorteios):
    freq_dezenas, freq_meses = calcular_frequencias(sorteios)
    dezenas_validas = [d for d, _ in freq_dezenas.most_common(20)]  # Top 20 mais frequentes
    meses_validos = [m for m, _ in freq_meses.most_common()]

    cartoes_gerados = []
    tentativas = 0
    max_tentativas = qtd * 100

    while len(cartoes_gerados) < qtd and tentativas < max_tentativas:
        tentativas += 1
        cartao = gerar_cartao(freq_dezenas, dezenas_validas, meses_validos)
        media_acertos = simular_acertos(cartao, sorteios)

        if media_acertos >= 4.5 and cartao not in cartoes_gerados:
            cartoes_gerados.append(cartao)

    return cartoes_gerados
