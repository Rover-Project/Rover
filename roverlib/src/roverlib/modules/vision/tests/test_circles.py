"""
Testes da detecção de círculos com imagens sintéticas (não precisa de câmera).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/modules/vision/tests
"""
import cv2
import numpy as np
import pytest

from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule

VERMELHO = (30, 30, 200)  # BGR


def imagem_com_circulo(raio, centro=(320, 300), tamanho=(640, 640)):
    img = np.full((tamanho[0], tamanho[1], 3), 200, np.uint8)
    cv2.circle(img, centro, raio, VERMELHO, -1)
    cv2.rectangle(img, (20, 20), (80, 60), VERMELHO, -1)  # objeto vermelho que não é círculo
    return img


@pytest.mark.parametrize("raio", [12, 30, 60, 150, 250])
def test_detecta_circulos_pequenos_e_grandes(raio):
    mask = ProcessingImage.color_dual_segmentation(imagem_com_circulo(raio))
    hough, _ = VisionModule.houghCircleDetect(mask)
    contour = VisionModule.circleCannyDetect(mask)

    for x, y, r in (hough, contour):
        assert abs(x - 320) <= 3 and abs(y - 300) <= 3
        assert abs(r - raio) <= max(3, raio * 0.1)


def test_hough_retorna_int_comum():
    mask = ProcessingImage.color_dual_segmentation(imagem_com_circulo(40))
    hough, _ = VisionModule.houghCircleDetect(mask)
    assert all(type(v) is int for v in hough)   # uint16 estourava em subtrações


def test_mascara_tem_o_tamanho_da_imagem():
    img = imagem_com_circulo(40, centro=(500, 100), tamanho=(480, 640))
    mask = ProcessingImage.color_dual_segmentation(img)
    assert mask.shape == (480, 640)
    x, y, r = VisionModule.circleCannyDetect(mask)
    assert (abs(x - 500), abs(y - 100)) <= (2, 2)


def test_sem_vermelho_nao_detecta():
    img = np.full((480, 640, 3), 200, np.uint8)
    cv2.circle(img, (320, 240), 60, (200, 60, 30), -1)   # círculo AZUL
    mask = ProcessingImage.color_dual_segmentation(img)
    assert VisionModule.houghCircleDetect(mask)[0] is None
    assert VisionModule.circleCannyDetect(mask) is None
