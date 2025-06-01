import random
from collections import Counter

def calcular_media_acertos(cartao, sorteios):
    acertos = []
    dezenas_cartao = set(cartao["dezenas"])
    for sorteio in sorteios[:20]:  # últimos 20 concursos
        dezenas_sorteadas = set(map(int, sorteio["dezenas"]))
        acertos.append(len(dezenas_cartao & dezenas_sorteadas))
    return sum(acertos) / len(acertos) if acertos else 0

def gerar_cartoes_otimizados(qtd, sorteios):
    if not sorteios:
        return []

    todas_dezenas = list(range(1, 32))
    meses_freq = Counter([s["mesSorte"] for s in sorteios])
    meses_comuns = [mes for mes, _ in meses_freq.most_common(6)]

    # Excluir cartões já sorteados
    cartoes_premiados = {tuple(sorted(map(int, s["dezenas"]))) for s in sorteios}

    # Frequência das dezenas
    freq = Counter()
    for s in sorteios:
        freq.update(map(int, s["dezenas"]))

    dezenas_mais_frequentes = [d for d, _ in freq.most_common(20)]
    dezenas_menos_frequentes = [d for d, _ in freq.most_common()][-12:]

    cartoes_validos = []
    tentativas = 0
    max_tentativas = qtd * 80

    while len(cartoes_validos) < qtd and tentativas < max_tentativas:
        tentativas += 1
        dezenas = sorted(random.sample(todas_dezenas, 7))
        if tuple(dezenas) in cartoes_premiados:
            continue

        # Filtros estatísticos
        if not (3 <= sum(1 for d in dezenas if d % 2 == 0) <= 5):  # pares
            continue
        if not (100 <= sum(dezenas) <= 170):  # soma total
            continue
        if len(set(dezenas) & set(dezenas_menos_frequentes)) < 3:  # ao menos 3 dezenas "frias"
            continue

        mes_da_sorte = random.choice(meses_comuns)
        cartao = {"dezenas": dezenas, "mes_da_sorte": mes_da_sorte}
        media_acertos = calcular_media_acertos(cartao, sorteios)
        if media_acertos >= 4:  # exige média mínima de 4 acertos simulados
            cartoes_validos.append(cartao)

    return cartoes_validos
