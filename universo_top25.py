from collections import Counter

class UniversoTop25Service:
    def __init__(self, sorteios, janela=30, top_n=25):
        self.sorteios = sorteios[:janela]
        self.top_n = top_n
        self.frequencias = self._calcular_frequencias()
        self.universo = self._extrair_top()

    def _calcular_frequencias(self):
        dezenas = []
        for s in self.sorteios:
            dezenas.extend(map(int, s["dezenas"]))
        return Counter(dezenas)

    def _extrair_top(self):
        return [
            d for d, _ in self.frequencias.most_common(self.top_n)
        ]

    def niveis(self):
        # Divide em 3 camadas ocultas
        return {
            "alto": self.universo[:8],
            "medio": self.universo[8:16],
            "baixo": self.universo[16:25]
        }
