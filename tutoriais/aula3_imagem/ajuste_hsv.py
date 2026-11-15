"""
Aula 3 - Ajuste interativo de limiares HSV com a câmera.

Abre a câmera (webcam no PC, câmera do Rover na Raspberry Pi) e mostra a máscara
de segmentação ao vivo. Use os controles deslizantes para encontrar a faixa HSV de
um objeto. 'q' sai e imprime os valores escolhidos.

Executar (na pasta tutoriais/):  python aula3_imagem/ajuste_hsv.py
Precisa de uma câmera e de uma tela (não funciona por SSH sem interface gráfica).
"""
from pathlib import Path

import cv2

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[1] / "config_visao.yaml"
JANELA = "Ajuste HSV"
CONTROLES = [("H min", 0, 179), ("H max", 10, 179), ("S min", 120, 255),
             ("S max", 255, 255), ("V min", 50, 255), ("V max", 255, 255)]

with Rover.from_config(CONFIG) as rover:
    camera = rover.camera            # erro claro se não houver câmera
    camera.set_format("hsv")         # a câmera já entrega os frames em HSV

    cv2.namedWindow(JANELA)
    for nome, inicial, maximo in CONTROLES:
        cv2.createTrackbar(nome, JANELA, inicial, maximo, lambda _: None)

    while True:
        hsv = camera.get_frame()
        if hsv is None:
            continue
        v = [cv2.getTrackbarPos(nome, JANELA) for nome, _, _ in CONTROLES]
        mascara = cv2.inRange(hsv, (v[0], v[2], v[4]), (v[1], v[3], v[5]))

        cv2.imshow(JANELA, mascara)
        cv2.imshow("Camera", cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print(f"Faixa escolhida: inferior=({v[0]}, {v[2]}, {v[4]})  superior=({v[1]}, {v[3]}, {v[5]})")
    cv2.destroyAllWindows()
