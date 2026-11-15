"""
Aula 5 - O Rover gira para manter uma bola vermelha no centro da imagem.

Malha fechada: câmera -> segmentação -> centroide -> erro -> PID -> motores.
Inclui zona morta no erro (perto do centro, não corrige) e para os motores se
perder o objeto.

Executar (na pasta tutoriais/):  python aula5_controle/seguir_objeto.py
Precisa de uma câmera (webcam no PC ou a do Rover) e de uma tela. 'q' sai.
No PC, os motores são simulados: observe os comandos no terminal.
"""
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlador import PID  # noqa: E402
from roverlib import Rover, ProcessingImage  # noqa: E402

CONFIG = Path(__file__).resolve().parents[1] / "config_visao.yaml"

KP, KI, KD = 40, 20, 0        # ganhos (comece pela simulação: sintonia.py)
ZONA_MORTA_ERRO = 0.05        # |erro| menor que isso: considera centralizado
VELOCIDADE_MAXIMA = 60        # limita a velocidade de giro
AREA_MINIMA = 0.003           # fração da imagem ocupada pelo vermelho para valer como objeto

pid = PID(KP, KI, KD, limite=VELOCIDADE_MAXIMA)


def erro_horizontal(frame):
    """Erro normalizado [-1, 1] do centroide do vermelho, ou None se não houver objeto."""
    mascara = ProcessingImage.color_segmentation(frame)
    m = cv2.moments(mascara, binaryImage=True)
    altura, largura = mascara.shape
    if m["m00"] < AREA_MINIMA * largura * altura:
        return None, mascara
    cx = m["m10"] / m["m00"]
    return (cx - largura / 2) / (largura / 2), mascara


with Rover.from_config(CONFIG) as rover:
    camera = rover.camera
    anterior = time.monotonic()

    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        agora = time.monotonic()
        dt, anterior = agora - anterior, agora

        erro, mascara = erro_horizontal(frame)
        if erro is None:
            rover.move.stop()                 # perdeu o objeto: para e zera o PID
            pid.reiniciar()
            texto = "sem objeto"
        else:
            if abs(erro) < ZONA_MORTA_ERRO:
                erro = 0.0
            u = pid(erro, dt)
            # erro > 0: objeto à direita -> girar para a direita (roda esquerda à frente)
            rover.move.move(speed_right=-u, speed_left=u)
            texto = f"erro={erro:+.2f}  u={u:+.0f}"

        cv2.putText(frame, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Seguir objeto", frame)
        cv2.imshow("Mascara", mascara)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()
