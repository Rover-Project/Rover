from picamera2 import Picamera2
import cv2

# Inicializa a câmera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

while True:
        # Captura um frame (imagem atual da câmera)
        frame = picam2.capture_array()

        # Mostra na tela
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Camera em Loop", frame_bgr)

        # Sai se apertar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()

# O resultado esperado é a visualização de um vídeo ao vivo, com baixa latência, que permanece em execução até que o usuário pressione a tecla q para encerrar.

