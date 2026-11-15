"""
Cenas sintéticas para as aulas de visão (3, 4 e 5).

Gera imagens em BGR com objetos de posição, tamanho e cor conhecidos, para que os
algoritmos possam ser testados e avaliados sem câmera (a "verdade" é conhecida).

    from cena import gerar_cena, VERMELHO
    img, objetos = gerar_cena(objetos=[Objeto("circulo", (320, 240), 60, VERMELHO)])
"""
from dataclasses import dataclass

import cv2
import numpy as np

# Cores em BGR (a ordem do OpenCV)
VERMELHO = (30, 30, 200)
AZUL = (200, 80, 30)
VERDE = (40, 170, 40)
AMARELO = (30, 200, 220)


@dataclass
class Objeto:
    tipo: str            # "circulo" ou "quadrado"
    centro: tuple        # (x, y) em pixels
    tamanho: int         # raio do círculo ou metade do lado do quadrado
    cor: tuple           # BGR

    def desenhar(self, img, cor=None):
        cor = self.cor if cor is None else cor
        x, y = self.centro
        if self.tipo == "circulo":
            cv2.circle(img, (int(x), int(y)), int(self.tamanho), cor, -1)
        else:
            t = int(self.tamanho)
            cv2.rectangle(img, (int(x) - t, int(y) - t), (int(x) + t, int(y) + t), cor, -1)

    def mascara(self, largura, altura):
        """Máscara binária (255 dentro do objeto) do tamanho da imagem."""
        m = np.zeros((altura, largura), np.uint8)
        self.desenhar(m, 255)
        return m


CENA_PADRAO = [
    Objeto("circulo", (220, 260), 60, VERMELHO),
    Objeto("circulo", (470, 150), 40, AZUL),
    Objeto("quadrado", (480, 360), 45, VERDE),
    Objeto("quadrado", (110, 110), 35, AMARELO),
]


def gerar_cena(largura=640, altura=480, objetos=None, brilho=1.0, ruido=8.0, seed=0):
    """
    Desenha os objetos sobre um fundo com gradiente e aplica iluminação e ruído.

    Args:
        objetos (list[Objeto]): objetos da cena. Padrão: CENA_PADRAO.
        brilho (float): fator de iluminação (1.0 = normal; 0.4 = cena escura).
        ruido (float): desvio padrão do ruído gaussiano, em níveis de cinza.
        seed (int): semente do ruído (mesma semente = mesma imagem).

    Returns:
        (imagem BGR uint8, lista de objetos)
    """
    objetos = CENA_PADRAO if objetos is None else objetos
    rng = np.random.default_rng(seed)

    # Fundo: gradiente horizontal de cinza, como uma parede iluminada de lado
    gradiente = np.linspace(90, 200, largura, dtype=np.float32)
    img = np.repeat(gradiente[None, :, None], altura, axis=0).repeat(3, axis=2)
    img = img.astype(np.uint8)

    for obj in objetos:
        obj.desenhar(img)

    img = img.astype(np.float32) * brilho + rng.normal(0, ruido, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8), objetos
