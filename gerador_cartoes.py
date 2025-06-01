import random

def gerar_cartoes_otimizados(qtd, sorteios):
    def desempenho_simulado(cartao):
        acertos = 0
        for s in sorteios[:20]:  # usa últimos 20 concursos
            acertos += len(set(cartao['dezenas']) & set(s['dezenas']))
        return acertos / 20

    todos_cartoes = []
    tentativas = 0
    while len(todos_cartoes) < qtd and tentativas < 1000:
        dezenas = random.sample(range(1, 32), 7)
        dezenas.sort()
        mesSorte = random.choice([
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ])
        cartao = {"dezenas": dezenas, "mesSorte": mesSorte}
        score = desempenho_simulado(cartao)

        if score >= 4.0:  # só aceita se média de acertos for 4 ou mais
            todos_cartoes.append(cartao)

        tentativas += 1

    # Se nenhum cartão atingiu o critério, retorna os melhores abaixo do limite
    if len(todos_cartoes) == 0:
        candidatos = []
        for _ in range(500):
            dezenas = random.sample(range(1, 32), 7)
            dezenas.sort()
            mesSorte = random.choice([
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ])
            cartao = {"dezenas": dezenas, "mesSorte": mesSorte}
            score = desempenho_simulado(cartao)
            candidatos.append((cartao, score))

        # ordena pelos melhores scores
        candidatos.sort(key=lambda x: x[1], reverse=True)
        todos_cartoes = [c[0] for c in candidatos[:qtd]]

    return todos_cartoes
