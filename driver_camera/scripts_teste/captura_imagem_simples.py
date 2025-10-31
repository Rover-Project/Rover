from picamera2 import Picamera2
import time
import os

# Intervalo entre fotos em segundos
INTERVALO = 5   # tire uma foto a cada 5s

# Criar pasta se não existir
pasta = "timelapse"
os.makedirs(pasta, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration({"size": (1920, 1080)})
picam2.configure(config)
picam2.start()

print("Timelapse iniciado. Pressione Ctrl+C para parar.")

contador = 1
try:
    while True:
        nome_arquivo = f"{pasta}/foto_{contador:04d}.jpg"
        picam2.capture_file(nome_arquivo)
        print(f"📸 Foto capturada: {nome_arquivo}")
        contador += 1
        time.sleep(INTERVALO)

except KeyboardInterrupt:
    print("\nTimelapse finalizado.")
    picam2.stop()
