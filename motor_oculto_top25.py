import random

class MotorOcultoTop25:
    def __init__(self, universo_service):
        self.niveis = universo_service.niveis()

    def gerar_cartao(self):
        dezenas = set()

        # Distribuição estrutural oculta
        qtd_alto = random.choice([2, 3])
        qtd_medio = random.choice([2, 3])
        qtd_baixo = 7 - (qtd_alto + qtd_medio)

        dezenas.update(random.sample(self.niveis["alto"], qtd_alto))
        dezenas.update(random.sample(self.niveis["medio"], qtd_medio))
        dezenas.update(random.sample(self.niveis["baixo"], qtd_baixo))

        return sorted(dezenas)

    @staticmethod
    def ajustar_cartao(dezenas):
        soma = sum(dezenas)
        pares = sum(1 for d in dezenas if d % 2 == 0)

        if not (70 <= soma <= 95):
            return None
        if pares not in (3, 4):
            return None

        return dezenas
