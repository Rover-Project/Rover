"""
Aula 4 - Avaliação quantitativa dos detectores de círculos da RoverLib.

Gera cenas sintéticas com uma bola vermelha de posição e raio aleatórios (e outros
objetos como distração) e mede, para cada detector:

- taxa de acerto: centro a menos de 10 px e raio com erro menor que 20%;
- erro médio do centro (px) e do raio (%), considerando só os acertos.

Executar (na pasta tutoriais/):  python aula4_deteccao/comparar_detectores.py
"""
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cena import gerar_cena, Objeto, VERMELHO, AZUL, VERDE  # noqa: E402
from roverlib import ProcessingImage, VisionModule  # noqa: E402

CENAS_POR_CONDICAO = 40


def cena_aleatoria(rng, brilho, ruido, seed):
    raio = rng.randint(15, 110)
    x = rng.randint(raio, 640 - raio)
    y = rng.randint(raio, 480 - raio)
    bola = Objeto("circulo", (x, y), raio, VERMELHO)
    distracoes = [Objeto("circulo", (rng.randint(40, 600), rng.randint(40, 440)), 30, AZUL),
                  Objeto("quadrado", (rng.randint(40, 600), rng.randint(40, 440)), 35, VERDE)]
    img, _ = gerar_cena(objetos=distracoes + [bola], brilho=brilho, ruido=ruido, seed=seed)
    return img, bola


def hough(mascara):
    return VisionModule.houghCircleDetect(mascara)[0]


def contorno(mascara):
    return VisionModule.circleCannyDetect(mascara)


def avaliar(detector, condicao):
    rng = random.Random(42)                       # mesmas cenas para todos os detectores
    acertos, erros_centro, erros_raio = 0, [], []
    for i in range(CENAS_POR_CONDICAO):
        img, bola = cena_aleatoria(rng, seed=i, **condicao)
        mascara = ProcessingImage.color_dual_segmentation(img)
        det = detector(mascara)
        if det is None:
            continue
        x, y, r = det
        erro_c = math.dist((x, y), bola.centro)
        erro_r = abs(r - bola.tamanho) / bola.tamanho
        if erro_c < 10 and erro_r < 0.2:
            acertos += 1
            erros_centro.append(erro_c)
            erros_raio.append(100 * erro_r)
    media = lambda v: float(np.mean(v)) if v else float("nan")   # noqa: E731
    return 100 * acertos / CENAS_POR_CONDICAO, media(erros_centro), media(erros_raio)


if __name__ == "__main__":
    condicoes = {
        "boa iluminação": dict(brilho=1.0, ruido=8),
        "ruído forte": dict(brilho=1.0, ruido=30),
        "cena escura": dict(brilho=0.5, ruido=8),
    }
    detectores = {"Hough": hough, "Contorno": contorno}

    print(f"{CENAS_POR_CONDICAO} cenas por condição\n")
    print(f"{'condição':16s} {'detector':9s} {'acertos':>8s} {'erro centro':>12s} {'erro raio':>10s}")
    for nome_c, condicao in condicoes.items():
        for nome_d, detector in detectores.items():
            taxa, ec, er = avaliar(detector, condicao)
            print(f"{nome_c:16s} {nome_d:9s} {taxa:7.0f}% {ec:9.1f} px {er:8.1f} %")
