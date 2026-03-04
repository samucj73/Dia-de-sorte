from itertools import combinations
from collections import Counter
import random

class PadroesOcultosService:
    def __init__(self, sorteios):
        self.sorteios = sorteios
        self.dezenas_por_concurso = [
            list(map(int, s["dezenas"])) for s in sorteios
        ]

        self.pares = self._pares_frequentes()
        self.trincas = self._trincas_frequentes()
        self.ancoras = self._ancoras()

    def _pares_frequentes(self):
        c = Counter()
        for dezenas in self.dezenas_por_concurso:
            for p in combinations(sorted(dezenas), 2):
                c[p] += 1
        return [p for p, v in c.items() if v >= 18]

    def _trincas_frequentes(self):
        c = Counter()
        for dezenas in self.dezenas_por_concurso:
            for t in combinations(sorted(dezenas), 3):
                c[t] += 1
        return [t for t, v in c.items() if v >= 7]

    def _ancoras(self):
        c = Counter()
        for dezenas in self.dezenas_por_concurso:
            for d in dezenas:
                c[d] += 1

        media = sum(c.values()) / len(c)
        return [d for d, v in c.items() if v >= media]

    def sortear_bloco_oculto(self):
        escolha = random.choice(["par", "trinca", "ancora"])

        if escolha == "trinca" and self.trincas:
            return set(random.choice(self.trincas))

        if escolha == "par" and self.pares:
            return set(random.choice(self.pares))

        if self.ancoras:
            return {random.choice(self.ancoras)}

        return set()

    def sugerir_dezenas(self):
        return list(self.sortear_bloco_oculto())
