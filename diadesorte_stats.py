import os
import json
from collections import Counter
from diadesorte_api import baixar_ultimos_sorteios

def carregar_sorteios():
    caminho = "sorteios_diadesorte.json"

    if not os.path.exists(caminho):
        print("Arquivo de sorteios não encontrado. Baixando da API...")
        sorteios = baixar_ultimos_sorteios()
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(sorteios, f, indent=4, ensure_ascii=False)
    else:
        with open(caminho, "r", encoding="utf-8") as f:
            sorteios = json.load(f)

    return sorteios

def frequencia_dezenas(sorteios):
    cont = Counter()
    for s in sorteios:
        if "dezenas" in s:
            cont.update(map(int, s["dezenas"]))
    return dict(cont.most_common())

def frequencia_meses(sorteios):
    cont = Counter()
    for s in sorteios:
        mes = s.get("mesSorte")  # Corrigido o nome da chave
        if mes:
            cont[mes] += 1
    return dict(cont.most_common())

def pares_impares(sorteios):
    distribuicoes = []
    for s in sorteios:
        dezenas = list(map(int, s["dezenas"]))
        pares = sum(1 for d in dezenas if d % 2 == 0)
        impares = 7 - pares
        distribuicoes.append({"pares": pares, "ímpares": impares})
    return distribuicoes

def soma_dezenas(sorteios):
    return [sum(map(int, s["dezenas"])) for s in sorteios]

def sequencias_consecutivas(sorteios):
    resultados = []
    for s in sorteios:
        dezenas = sorted(map(int, s["dezenas"]))
        sequencias = []
        seq = [dezenas[0]]
        for i in range(1, len(dezenas)):
            if dezenas[i] == dezenas[i-1] + 1:
                seq.append(dezenas[i])
            else:
                if len(seq) > 1:
                    sequencias.append(seq)
                seq = [dezenas[i]]
        if len(seq) > 1:
            sequencias.append(seq)
        resultados.append(sequencias)
    return resultados

def repeticao_entre_concursos(sorteios):
    repeticoes = []
    for i in range(1, len(sorteios)):
        atual = set(map(int, sorteios[i]["dezenas"]))
        anterior = set(map(int, sorteios[i-1]["dezenas"]))
        repeticoes.append(len(atual & anterior))
    return repeticoes
