import requests
import time
import json
import os

def obter_concurso(concurso):
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/{concurso}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter concurso {concurso}: {e}")
        return None

def obter_ultimo_concurso():
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        dados = response.json()
        return dados["numero"]
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter último concurso: {e}")
        return None

def obter_ultimos_30_concursos():
    ultimo = obter_ultimo_concurso()
    if not ultimo:
        return []

    ultimos_sorteios = []
    for n in range(ultimo, ultimo - 30, -1):
        dados = obter_concurso(n)
        if dados:
            sorteio = {
                "concurso": dados["numero"],
                "data": dados["dataApuracao"],
                "dezenas": dados["listaDezenas"],
                "mes_sorte": dados["listaMesesSorte"]
            }
            ultimos_sorteios.append(sorteio)
        time.sleep(0.3)  # evita sobrecarregar a API

    return ultimos_sorteios

def salvar_em_json(dados, caminho_arquivo="ultimos_sorteios_dia_de_sorte.json"):
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")

# Execução principal
if __name__ == "__main__":
    ultimos_sorteios = obter_ultimos_30_concursos()
    salvar_em_json(ultimos_sorteios)
