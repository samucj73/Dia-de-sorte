import requests

def baixar_ultimos_sorteios(qtd=30):
    url_ultimo = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/ultimos"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.loteriaseresultados.com.br/",
        "Origin": "https://www.loteriaseresultados.com.br"
    }

    try:
        r = requests.get(url_ultimo, headers=headers, timeout=10)
        r.raise_for_status()
        ultimo_num = r.json()["numero"]

        sorteios = []
        for num in range(ultimo_num, ultimo_num - qtd, -1):
            url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/{num}"
            r_sorteio = requests.get(url, headers=headers, timeout=10)
            r_sorteio.raise_for_status()
            data = r_sorteio.json()

            dezenas = data.get("listaDezenasSorteadasOrdemSorteio", [])
            mes_sorte = data.get("mesSorte", None)

            if dezenas:
                sorteios.append({
                    "concurso": num,
                    "dezenas": dezenas,
                    "mes_sorte": mes_sorte
                })
        return sorteios
    except Exception as e:
        print(f"Erro ao baixar sorteios: {e}")
        return []
