from diadesorte_stats import carregar_sorteios
import random

def gerar_cartoes_otimizados(qtd=5):
    sorteios = carregar_sorteios()
    if not sorteios:
        raise ValueError("Não há sorteios disponíveis.")

    contagem = {}
    for s in sorteios:
        for dezena in s["dezenas"]:
            contagem[dezena] = contagem.get(dezena, 0) + 1

    mais_frequentes = sorted(contagem, key=contagem.get, reverse=True)[:20]
    meses = [s["mes_sorte"] for s in sorteios if s["mes_sorte"]]

    cartoes = []
    for _ in range(qtd):
        dezenas = sorted(random.sample(mais_frequentes, 7))
        mes = random.choice(meses) if meses else "Janeiro"
        cartoes.append({"dezenas": dezenas, "mes_sorte": mes})

    return cartoes
