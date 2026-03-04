from universo_top25 import UniversoTop25Service
from motor_oculto_top25 import MotorOcultoTop25

class EstrategiaOcultaTop25:
    nome = "🧠 Oculta Top-25 (Últimos 30)"

    def gerar(self, qtd, sorteios):
        universo = UniversoTop25Service(sorteios)
        motor = MotorOcultoTop25(universo)

        cartoes = []
        tentativas = 0

        while len(cartoes) < qtd and tentativas < 20000:
            tentativas += 1

            dezenas = motor.gerar_cartao()
            dezenas_validas = motor.ajustar_cartao(dezenas)

            if dezenas_validas:
                cartoes.append({
                    "dezenas": [str(d).zfill(2) for d in dezenas_validas],
                    "mesSorte": None
                })

        return cartoes
