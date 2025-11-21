from picamera2 import Picamera2
from datetime import datetime
import os

# Inicializa a câmera
picam2 = Picamera2()
rotacao = 90
cfg = picam2.create_still_configuration(main={"size": (3280, 2464)}, transform=Transform(rotation=rotacao))
picam2.configure(cfg)
picam2.start()

# Pasta onde as fotos serão salvas
pasta = "/home/rover/Imagens/TestesDoNovoSensor"
os.makedirs(pasta, exist_ok=True)

print("=== Sistema de Captura de Fotos ===")
print("Pressione ENTER para capturar uma foto.")
print("Digite 'q' e pressione ENTER para sair.\n")

while True:
    comando = input("Comando: ")

    if comando.lower() == "q":
        print("Encerrando o programa...")
        break

    # Capturar foto com data e hora
    nome = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
    caminho = os.path.join(pasta, nome)

    picam2.capture_file(caminho)
    print(f"Foto capturada e salva em: {caminho}")

picam2.stop()
