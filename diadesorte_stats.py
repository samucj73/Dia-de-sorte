import json
from collections import Counter

def carregar_sorteios(caminho="ultimos_sorteios_dia_de_sorte.json"):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def frequencia_dezenas(sorteios):
    todas = [dez for sorteio in sorteios for dez in sorteio["dezenas"]]
    return Counter(todas).most_common()

def frequencia_meses(sorteios):
    todos = [mes for sorteio in sorteios for mes in sorteio["mes_sorte"]]
    return Counter(todos).most_common()

def pares_impares(sorteios):
    distribuicao = []
    for sorteio in sorteios:
        dezenas = list(map(int, sorteio["dezenas"]))
        pares = sum(1 for d in dezenas if d % 2 == 0)
        impares = 7 - pares
        distribuicao.append({"pares": pares, "ímpares": impares})
    return distribuicao

def soma_dezenas(sorteios):
    return [sum(map(int, s["dezenas"])) for s in sorteios]

def sequencias_consecutivas(sorteios):
    def contar_seq(dezenas):
        dezenas = sorted(map(int, dezenas))
        seq = 0
        contagem = []
        for i in range(len(dezenas) - 1):
            if dezenas[i] + 1 == dezenas[i + 1]:
                seq += 1
            else:
                if seq > 0:
                    contagem.append(seq + 1)
                seq = 0
        if seq > 0:
            contagem.append(seq + 1)
        return contagem
    return [contar_seq(s["dezenas"]) for s in sorteios]

def repeticao_entre_concursos(sorteios):
    repeticoes = []
    for i in range(1, len(sorteios)):
        atual = set(sorteios[i]["dezenas"])
        anterior = set(sorteios[i - 1]["dezenas"])
        repetidas = atual.intersection(anterior)
        repeticoes.append(len(repetidas))
    return repeticoes

# Exemplo de uso
if __name__ == "__main__":
    sorteios = carregar_sorteios()

    print("\n🔢 Frequência das dezenas:")
    for dez, freq in frequencia_dezenas(sorteios):
        print(f"{dez}: {freq}x")

    print("\n📅 Frequência dos meses da sorte:")
    for mes, freq in frequencia_meses(sorteios):
        print(f"{mes}: {freq}x")

    print("\n➗ Distribuição pares/ímpares:")
    for i, dist in enumerate(pares_impares(sorteios), 1):
        print(f"Concurso {i}: {dist}")

    print("\n🔢 Soma das dezenas por concurso:")
    print(soma_dezenas(sorteios))

    print("\n📶 Sequências consecutivas:")
    for i, seqs in enumerate(sequencias_consecutivas(sorteios), 1):
        print(f"Concurso {i}: {seqs}")

    print("\n🔁 Repetições de dezenas em relação ao concurso anterior:")
    print(repeticao_entre_concursos(sorteios))
