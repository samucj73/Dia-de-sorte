import requests

def baixar_ultimos_sorteios(qtd=30):
    url_base = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

    concursos = []
    ultimo = buscar_ultimo_concurso()
    
    if ultimo == 0:
        print("❌ Não foi possível obter o número do último concurso.")
        return []

    for n in range(ultimo, ultimo - qtd, -1):
        url = url_base + str(n)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                dezenas = data.get("listaDezenasSorteadasOrdemSorteio", [])
                mes_sorte = data.get("listaDezenas", [])
                if dezenas:
                    concursos.append({
                        "concurso": n,
                        "dezenas": dezenas,
                        "mes_sorte": mes_sorte[0] if mes_sorte else None
                    })
        except Exception as e:
            print(f"❌ Erro ao obter concurso {n}: {e}")

    return concursos

def buscar_ultimo_concurso():
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/ultimos"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return int(data["numero"])
    except Exception as e:
        print(f"❌ Erro ao buscar último concurso: {e}")

    return 0
