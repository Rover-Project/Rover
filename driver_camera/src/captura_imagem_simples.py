from picamera2 import Picamera2
import cv2

# Inicializa a câmera picam2 = Picamera2()

# Configura a resolução
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Inicia captura
picam2.start()

# Captura uma imagem
frame = picam2.capture_array()

# Mostra a imagem capturada
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
cv2.imshow("Imagem Capturada", frame_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Resultado esperado: O código deve abrir uma janela com a imagem capturada pela câmera. Se aparecer, está tudo certo com a instalação e configuração do software.
