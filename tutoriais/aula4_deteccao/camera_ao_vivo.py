"""
Aula 4 - Detecção de uma bola vermelha ao vivo.

Aplica a segmentação e os dois detectores da RoverLib aos frames da câmera e
desenha o resultado: Hough em verde, contorno em azul.

Executar (na pasta tutoriais/):  python aula4_deteccao/camera_ao_vivo.py
Precisa de uma câmera (webcam no PC ou a do Rover) e de uma tela. 'q' sai.
"""
from pathlib import Path

import cv2

from roverlib import Rover, ProcessingImage, VisionModule

CONFIG = Path(__file__).resolve().parents[1] / "config_visao.yaml"

with Rover.from_config(CONFIG) as rover:
    camera = rover.camera
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue

        mascara = ProcessingImage.color_dual_segmentation(frame)
        hough, _ = VisionModule.houghCircleDetect(mascara)
        contorno = VisionModule.circleCannyDetect(mascara)

        for circulo, cor in ((hough, (0, 255, 0)), (contorno, (255, 0, 0))):
            if circulo is not None:
                x, y, r = circulo
                cv2.circle(frame, (x, y), r, cor, 2)
                cv2.circle(frame, (x, y), 3, cor, -1)

        cv2.imshow("Deteccao (verde: Hough, azul: contorno)", frame)
        cv2.imshow("Mascara", mascara)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()
