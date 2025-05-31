import requests

def baixar_ultimos_sorteios(qtd=30):
    """
    Baixa os últimos 'qtd' sorteios da Dia de Sorte usando a API alternativa pública.
    Retorna uma lista de dicionários com os dados dos concursos.
    """
    url = "https://loteriascaixa-api.vercel.app/api/diadesorte"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()
        concursos = dados.get("concursos", [])
        if not concursos:
            print("Nenhum concurso encontrado na API.")
            return []
        # Retorna os últimos 'qtd' concursos (ou menos se não houver tantos)
        return concursos[:qtd]
    except Exception as e:
        print(f"Erro ao baixar sorteios: {e}")
        return []
