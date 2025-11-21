

from picamera2 import Picamera2, Transform
from datetime import datetime
import os
import keyboard

picam2 = Picamera2()

rotacao = 90  # ALTERE PARA 0, 90, 180 OU 270

cfg = picam2.create_still_configuration(
    main={"size": (3280, 2464)},
    transform=Transform(rotation=rotacao)
)

picam2.configure(cfg)
picam2.start()

pasta = "/home/rover/Imagens/TestesDoNovoSensor"
os.makedirs(pasta, exist_ok=True)

print("Pressione ESPAÇO para capturar, 'q' para sair.")

while True:
    if keyboard.is_pressed('space'):
        nome = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
        caminho = os.path.join(pasta, nome)
        picam2.capture_file(caminho)
        print("Foto salva:", caminho)

        while keyboard.is_pressed('space'):
            pass  # impede múltiplos disparos

    if keyboard.is_pressed('q'):
        break

picam2.stop()
