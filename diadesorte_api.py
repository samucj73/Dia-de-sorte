import requests

BASE_URL = "https://loteriascaixa-api.herokuapp.com/api/diadesorte/"

def baixar_concurso(numero_concurso):
    """
    Baixa os dados do concurso da Dia de Sorte pelo número do concurso.
    Retorna dict com dados do concurso ou None se não existir.
    """
    url = f"{BASE_URL}{numero_concurso}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()
        # Se a resposta for um dict com erro ou vazio, trate aqui
        if 'error' in dados or not dados:
            return None
        return dados
    except requests.RequestException:
        return None

def baixar_ultimos_sorteios(qtd=30):
    """
    Baixa os últimos 'qtd' sorteios da Dia de Sorte, retornando lista de dicts.
    Tenta baixar do último concurso disponível para trás.
    """
    # Primeiro, buscar o último concurso (endpoint /latest)
    try:
        response = requests.get(f"{BASE_URL}latest", timeout=10)
        response.raise_for_status()
        ultimo = response.json()
        ultimo_num = ultimo.get("concurso")
        if not ultimo_num:
            return []
    except requests.RequestException:
        return []

    sorteios = []
    concurso_atual = ultimo_num

    while len(sorteios) < qtd and concurso_atual > 0:
        dados = baixar_concurso(concurso_atual)
        if dados:
            sorteios.append(dados)
        else:
            # Se não encontrou, pode ser concurso cancelado ou inexistente, apenas pula
            pass
        concurso_atual -= 1

    return sorteios
