"""
A câmera acompanha um objeto vermelho movendo os servos do pan-tilt.

- PAN (servo 360°): a VELOCIDADE do giro é proporcional à distância horizontal
  entre o objeto e o centro da imagem (controle proporcional).
- TILT (servo 180°): a cada frame, o ÂNGULO anda um pouco na direção do objeto,
  proporcionalmente à distância vertical.
"""
from pathlib import Path

import cv2

from roverlib import Rover, Config, ProcessingImage


class CameraTracker:
    def __init__(self, config_path: Path):
        tracking = Config(config_path).get("tracking") or {}
        self.kp_pan = tracking.get("kp_pan", 60)
        self.kp_tilt = tracking.get("kp_tilt", 6)
        self.deadzone = tracking.get("deadzone", 0.08)
        self.min_area = tracking.get("min_area", 0.005)

        self.rover = Rover.from_config(config_path)
        self.camera = self.rover.camera
        self.pan_tilt = self.rover.pan_tilt
        self.pan_tilt.center()

    def find_object(self, frame):
        """
        Procura a maior região vermelha da imagem.

        Returns:
            (erro_x, erro_y, mascara): erros normalizados entre -1 e 1 em relação ao
            centro da imagem (positivo = direita / baixo), ou (None, None, mascara).
        """
        mask = ProcessingImage.color_segmentation(frame)
        h, w = mask.shape[:2]

        moments = cv2.moments(mask, binaryImage=True)
        area = moments["m00"] / (w * h)
        if area < self.min_area:
            return None, None, mask

        cx = moments["m10"] / moments["m00"]
        cy = moments["m01"] / moments["m00"]
        error_x = (cx - w / 2) / (w / 2)
        error_y = (cy - h / 2) / (h / 2)
        return error_x, error_y, mask

    def follow(self, error_x, error_y):
        """Move os servos para trazer o objeto ao centro da imagem."""
        # PAN: velocidade proporcional ao erro horizontal
        if abs(error_x) > self.deadzone:
            self.pan_tilt.pan(self.kp_pan * error_x)
        else:
            self.pan_tilt.stop_pan()

        # TILT: objeto acima do centro (erro_y < 0) -> sobe a câmera
        if abs(error_y) > self.deadzone:
            self.pan_tilt.tilt_up(-self.kp_tilt * error_y)

    def run(self):
        print("Acompanhando objetos vermelhos. Pressione 'q' na janela para sair, 'c' para centralizar.")
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                continue

            error_x, error_y, mask = self.find_object(frame)

            if error_x is None:
                self.pan_tilt.stop_pan()  # perdeu o objeto: para de girar
                text = "Nenhum objeto"
            else:
                self.follow(error_x, error_y)
                text = f"erro x={error_x:+.2f} y={error_y:+.2f} | tilt={self.pan_tilt.tilt_angle:.0f} graus"

            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("Camera", frame)
            cv2.imshow("Mascara", mask)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                self.pan_tilt.center()

    def cleanup(self):
        print("Centralizando a câmera e desligando...")
        try:
            self.pan_tilt.center()
        finally:
            self.rover.cleanup()
            cv2.destroyAllWindows()
