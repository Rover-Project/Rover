"""
Aula 3 - Segmentação por cor: limiar em BGR x limiar em HSV.

Segmenta o círculo vermelho da cena sintética de duas formas e mede a qualidade
de cada uma com o IoU (interseção sobre união) em relação à máscara verdadeira,
variando a iluminação da cena.

Executar (na pasta tutoriais/):  python aula3_imagem/segmentacao.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cena import gerar_cena  # noqa: E402
from roverlib import ProcessingImage  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "saida"
SAIDA.mkdir(exist_ok=True)


def segmentar_bgr(img):
    """Limiar direto nos canais: 'muito vermelho, pouco verde e pouco azul'."""
    b, g, r = cv2.split(img)
    return ((r > 150) & (g < 90) & (b < 90)).astype(np.uint8) * 255


def segmentar_hsv(img):
    """Limiar na matiz: o vermelho fica nas duas pontas da escala (0-10 e 170-179)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    baixo = cv2.inRange(hsv, (0, 120, 50), (10, 255, 255))
    alto = cv2.inRange(hsv, (170, 120, 50), (179, 255, 255))
    return cv2.bitwise_or(baixo, alto)


def limpar(mascara):
    """Morfologia: abertura remove pontos isolados; fechamento tapa buracos."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)


def iou(a, b):
    a, b = a > 127, b > 127
    uniao = np.logical_or(a, b).sum()
    return np.logical_and(a, b).sum() / uniao if uniao else 1.0


if __name__ == "__main__":
    metodos = {
        "BGR": lambda im: segmentar_bgr(im),
        "HSV": lambda im: segmentar_hsv(im),
        "HSV + morfologia": lambda im: limpar(segmentar_hsv(im)),
        "RoverLib": lambda im: ProcessingImage.color_segmentation(im),
    }

    print(f"{'brilho':>7s} " + " ".join(f"{nome:>17s}" for nome in metodos))
    for brilho in (0.4, 0.6, 0.8, 1.0, 1.2):
        img, objetos = gerar_cena(brilho=brilho, ruido=12)
        verdade = objetos[0].mascara(img.shape[1], img.shape[0])     # o círculo vermelho
        valores = [iou(f(img), verdade) for f in metodos.values()]
        print(f"{brilho:7.1f} " + " ".join(f"{v:17.2f}" for v in valores))

        if brilho == 0.6:
            mascaras = [cv2.cvtColor(f(img), cv2.COLOR_GRAY2BGR) for f in metodos.values()]
            cv2.imwrite(str(SAIDA / "segmentacao_escura.png"),
                        cv2.resize(np.hstack([img] + mascaras), None, fx=0.4, fy=0.4))

    print(f"\nIoU = 1 é a segmentação perfeita. Exemplo com brilho 0.6 salvo em {SAIDA / 'segmentacao_escura.png'}")
