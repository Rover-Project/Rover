"""
Aula 2 - Filtrando um sinal de distância ruidoso.

Gera um sinal sintético do Lidar (o Rover se aproximando de uma parede), com
ruído gaussiano e leituras espúrias (outliers), e compara três filtros:
média móvel, mediana móvel e filtro exponencial.

Executar (na pasta tutoriais/):  python aula2_sensores/filtros.py
A figura é salva em aula2_sensores/saida/filtros.png.
"""
from collections import deque
from pathlib import Path
import statistics

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAIDA = Path(__file__).resolve().parent / "saida"
TAXA = 20            # leituras por segundo
DURACAO = 10         # segundos
RUIDO_CM = 2.0       # desvio padrão do ruído gaussiano
P_OUTLIER = 0.05     # probabilidade de uma leitura espúria


def sinal_sintetico(seed=1):
    """Distância real (150 cm -> 20 cm em DURACAO s) e a leitura ruidosa correspondente."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, DURACAO, 1 / TAXA)
    real = np.linspace(150, 20, t.size)
    medido = real + rng.normal(0, RUIDO_CM, t.size)
    espurias = rng.random(t.size) < P_OUTLIER
    medido[espurias] = rng.choice([0, 800], espurias.sum())   # reflexos e leituras perdidas
    return t, real, medido


class MediaMovel:
    def __init__(self, n=5):
        self.janela = deque(maxlen=n)

    def __call__(self, x):
        self.janela.append(x)
        return sum(self.janela) / len(self.janela)


class MedianaMovel:
    def __init__(self, n=5):
        self.janela = deque(maxlen=n)

    def __call__(self, x):
        self.janela.append(x)
        return statistics.median(self.janela)


class Exponencial:
    """y[k] = alfa * x[k] + (1 - alfa) * y[k-1]"""

    def __init__(self, alfa=0.3):
        self.alfa = alfa
        self.y = None

    def __call__(self, x):
        self.y = x if self.y is None else self.alfa * x + (1 - self.alfa) * self.y
        return self.y


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    t, real, medido = sinal_sintetico()

    filtros = {
        "média móvel (n=5)": MediaMovel(5),
        "mediana móvel (n=5)": MedianaMovel(5),
        "exponencial (alfa=0.3)": Exponencial(0.3),
    }
    saidas = {nome: [f(x) for x in medido] for nome, f in filtros.items()}

    print(f"{'sinal':28s} RMSE em relação à distância real")
    print(f"{'sem filtro':28s} {rmse(medido, real):7.1f} cm")
    for nome, y in saidas.items():
        print(f"{nome:28s} {rmse(y, real):7.1f} cm")

    plt.figure(figsize=(9, 5))
    plt.plot(t, medido, ".", color="0.7", label="leitura bruta")
    plt.plot(t, real, "k--", label="distância real")
    for nome, y in saidas.items():
        plt.plot(t, y, label=nome)
    plt.ylim(0, 200)
    plt.xlabel("tempo (s)")
    plt.ylabel("distância (cm)")
    plt.title("Filtros para o sinal do Lidar (outliers em 0 e 800 cm fora da escala)")
    plt.legend()
    plt.grid(True)
    arquivo = SAIDA / "filtros.png"
    plt.savefig(arquivo, dpi=120)
    print(f"Figura salva em {arquivo}")
