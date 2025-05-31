import requests

def baixar_ultimos_sorteios(qtd=30):
    """
    Baixa os últimos 'qtd' concursos do Dia de Sorte usando a API oficial da Caixa.
    Retorna uma lista de dicionários com dezenas e mês da sorte.
    """
    url_base = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

    concursos = []
    ultimo = buscar_ultimo_concurso()
    for n in range(ultimo, ultimo - qtd, -1):
        url = url_base + str(n)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                dezenas = data["listaDezenasSorteadasOrdemSorteio"]
                mes_sorte = data["listaDezenas"]
                concursos.append({
                    "concurso": n,
                    "dezenas": dezenas,
                    "mes_sorte": mes_sorte[0] if mes_sorte else None
                })
        except Exception as e:
            print(f"Erro ao obter concurso {n}: {e}")

    return concursos

def buscar_ultimo_concurso():
    """
    Retorna o número do último concurso disponível da Dia de Sorte.
    """
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/ultimos"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return int(data["numero"])
    except Exception as e:
        print(f"Erro ao buscar último concurso: {e}")

    return 0
