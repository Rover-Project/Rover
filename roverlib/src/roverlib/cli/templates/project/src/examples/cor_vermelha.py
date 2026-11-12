"""
Exemplo 2 - Câmera: destaca objetos vermelhos na imagem.

Antes: ative a seção "camera:" no config.yaml.
Execute na pasta do projeto:   python -m src.examples.cor_vermelha
Pressione "q" na janela da imagem para sair.
"""
from pathlib import Path

import cv2

from roverlib import Rover, ProcessingImage

CONFIG = Path(__file__).resolve().parents[2] / "config.yaml"


def main():
    with Rover.from_config(CONFIG) as rover:
        while True:
            frame = rover.camera.get_frame()
            if frame is None:
                continue

            # Máscara branca onde a imagem é vermelha
            mascara = ProcessingImage.color_segmentation(frame)
            porcentagem = 100 * cv2.countNonZero(mascara) / mascara.size

            cv2.putText(frame, f"Vermelho: {porcentagem:.1f}%", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Camera", frame)
            cv2.imshow("Mascara", mascara)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
