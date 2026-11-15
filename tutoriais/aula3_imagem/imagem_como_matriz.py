"""
Aula 3 - A imagem como matriz e os espaços de cor.

Gera uma cena sintética, mostra a estrutura do array NumPy e compara os valores
de um pixel em BGR e em HSV. Salva os canais de cada espaço de cor.

Executar (na pasta tutoriais/):  python aula3_imagem/imagem_como_matriz.py
As imagens são salvas em aula3_imagem/saida/.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # para importar cena.py
from cena import gerar_cena  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "saida"
SAIDA.mkdir(exist_ok=True)

img, objetos = gerar_cena()
print(f"forma: {img.shape}  (altura, largura, canais)   tipo: {img.dtype}")
print(f"valor mínimo {img.min()}, máximo {img.max()}, média {img.mean():.1f}")

# Um pixel é um vetor de 3 valores, na ordem B, G, R
x, y = objetos[0].centro                     # centro do círculo vermelho
b, g, r = img[y, x]                          # atenção: linha (y) primeiro, coluna (x) depois
print(f"\npixel ({x}, {y}) em BGR: B={b} G={g} R={r}")

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = hsv[y, x]
print(f"o mesmo pixel em HSV: H={h} (matiz, 0-179)  S={s} (saturação)  V={v} (brilho)")

# Mosaico com os canais de cada espaço de cor
def rotulo(canal, texto):
    c = cv2.cvtColor(canal, cv2.COLOR_GRAY2BGR)
    cv2.putText(c, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    return c

linha_bgr = np.hstack([rotulo(img[:, :, i], n) for i, n in enumerate("BGR")])
linha_hsv = np.hstack([rotulo(hsv[:, :, i], n) for i, n in enumerate("HSV")])
mosaico = np.vstack([linha_bgr, linha_hsv])

cv2.imwrite(str(SAIDA / "cena.png"), img)
cv2.imwrite(str(SAIDA / "canais.png"), cv2.resize(mosaico, None, fx=0.5, fy=0.5))
print(f"\nImagens salvas em {SAIDA}: cena.png e canais.png")
