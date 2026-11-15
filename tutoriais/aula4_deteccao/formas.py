"""
Aula 4 - Contornos, momentos e circularidade.

Encontra os objetos coloridos da cena sintética, calcula o centroide pelos
momentos da imagem e classifica cada um como círculo ou quadrado pela
circularidade C = 4*pi*A / P^2 (1 para o círculo perfeito, pi/4 para o quadrado).

Executar (na pasta tutoriais/):  python aula4_deteccao/formas.py
A imagem anotada é salva em aula4_deteccao/saida/formas.png.
"""
import math
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cena import gerar_cena  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "saida"
SAIDA.mkdir(exist_ok=True)
LIMIAR_CIRCULO = 0.85   # circularidade acima disso: círculo

img, objetos = gerar_cena()

# Os objetos são coloridos e o fundo é cinza: basta um limiar na saturação
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mascara = cv2.inRange(hsv, (0, 100, 40), (179, 255, 255))
mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
print(f"{len(contornos)} contornos encontrados\n")
print(f"{'centroide':>12s} {'área':>8s} {'perímetro':>10s} {'circularidade':>14s}  forma")

for c in contornos:
    m = cv2.moments(c)
    area = m["m00"]
    if area < 100:                       # descarta ruído
        continue
    cx, cy = m["m10"] / area, m["m01"] / area
    perimetro = cv2.arcLength(c, closed=True)
    circularidade = 4 * math.pi * area / perimetro ** 2
    forma = "círculo" if circularidade > LIMIAR_CIRCULO else "quadrado"
    print(f"({cx:5.0f},{cy:4.0f}) {area:8.0f} {perimetro:10.1f} {circularidade:14.3f}  {forma}")

    cv2.drawContours(img, [c], -1, (255, 255, 255), 2)
    cv2.circle(img, (int(cx), int(cy)), 4, (0, 0, 0), -1)
    cv2.putText(img, f"{forma} {circularidade:.2f}", (int(cx) - 50, int(cy) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

print("\nCentros verdadeiros:", [o.centro for o in objetos])
cv2.imwrite(str(SAIDA / "formas.png"), img)
print(f"Imagem anotada salva em {SAIDA / 'formas.png'}")
