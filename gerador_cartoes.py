import random
from diadesorte_stats import carregar_sorteios, frequencia_dezenas, frequencia_meses

def gerar_cartoes_otimizados(qtd=10):
    sorteios = carregar_sorteios()
    ultimos = sorteios[:30]
    ultimo = sorteios[0]

    # 🔥 Top 15 dezenas mais frequentes
    freq_dezenas = [int(d[0]) for d in frequencia_dezenas(ultimos)[:15]]

    # 🗓️ Top 4 meses mais sorteados
    meses_frequentes = [m[0] for m in frequencia_meses(ultimos)[:4]]

    # 🎯 Cartões válidos
    cartoes = set()
    tentativas = 0
    max_tentativas = 10000

    while len(cartoes) < qtd and tentativas < max_tentativas:
        dezenas = sorted(random.sample(freq_dezenas, 7))
        pares = sum(1 for d in dezenas if d % 2 == 0)
        soma = sum(dezenas)

        # ⚠️ Filtros matemáticos
        if not (3 <= pares <= 5):  # pares/ímpares
            tentativas += 1
            continue
        if not (100 <= soma <= 160):  # soma total
            tentativas += 1
            continue
        if contar_sequencias(dezenas) > 2:
            tentativas += 1
            continue

        # 💡 Repetição com último concurso
        repetidas = len(set(dezenas).intersection(map(int, ultimo["dezenas"])))
        if not (3 <= repetidas <= 5):
            tentativas += 1
            continue

        # 🚫 Evita cartão idêntico a sorteios anteriores
        if any(sorted(map(int, s["dezenas"])) == dezenas for s in sorteios):
            tentativas += 1
            continue

        cartoes.add(tuple(dezenas))
        tentativas += 1

    # 📅 Mês da sorte otimizado
    cartoes_finais = [{"dezenas": list(c), "mes_da_sorte": random.choice(meses_frequentes)} for c in cartoes]
    return cartoes_finais

def contar_sequencias(dezenas):
    dezenas = sorted(dezenas)
    seq = 0
    total = 0
    for i in range(len(dezenas) - 1):
        if dezenas[i] + 1 == dezenas[i + 1]:
            seq += 1
        else:
            if seq > 0:
                total += 1
            seq = 0
    if seq > 0:
        total += 1
    return total

# Exemplo de uso
if __name__ == "__main__":
    cartoes = gerar_cartoes_otimizados(10)
    for i, cartao in enumerate(cartoes, 1):
        print(f"Cartão {i}: {cartao['dezenas']} | Mês da Sorte: {cartao['mes_da_sorte']}")
