from picamera2 import Picamera2
from datetime import datetime
import os
import cv2

# Criar pasta de destino
pasta = "/home/rover/Imagens/TestesDoNovoSensor"
os.makedirs(pasta, exist_ok=True)

# Inicializar câmera
picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"size": (3280, 2464)},
    transform={"rotation": 180}  # 0, 90, 180, 270
)

picam2.configure(config)
picam2.start()

print("\n--- Captura de Imagens ---")
print("Pressione '1' para tirar foto")
print("Pressione 'q' para sair\n")

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord('1'):
        nome = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
        caminho = os.path.join(pasta, nome)
        picam2.capture_file(caminho)
        print(f"Foto salva em: {caminho}")

    elif key == ord('q'):
        print("Encerrando captura...")
        break

picam2.stop()
cv2.destroyAllWindows()
