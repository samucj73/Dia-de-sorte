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

    todas_dezenas = list(range(1, 32))
    dezenas_frequentes = sorted(freq_dezenas, key=freq_dezenas.get, reverse=True)[:20]
    meses_frequentes = list(freq_meses.keys())

    cartoes = []
    tentativas = 0

    while len(cartoes) < qtd and tentativas < 1000:
        tentativas += 1
        dezenas = sorted(random.sample(dezenas_frequentes, 7))
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)

        # Restrições
        if not (min_soma <= soma <= max_soma):
            continue
        if abs(pares - media_pares) > 2:
            continue
        if len(set(dezenas) & set(ultimas_dezenas)) > 4:
            continue

        # Limita sequências consecutivas a no máximo 2
        consecutivas = 0
        for i in range(1, 7):
            if dezenas[i] == dezenas[i - 1] + 1:
                consecutivas += 1
        if consecutivas > 2:
            continue

        mes = random.choice(meses_frequentes) if meses_frequentes else "Janeiro"
        cartoes.append({"dezenas": dezenas, "mesSorte": mes})

    return cartoes
