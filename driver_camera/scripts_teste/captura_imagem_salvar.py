from picamera2 import Picamera2, Preview
import time
from pathlib import Path
import sys

try:
    path = Path.home() / sys.argv[1] # recupera um parametro passado por linha de comando

except Exception:
    path = "foto.jpg" # Salva nessa pasta 

picam2 = Picamera2() # Inicializa a camera
camera_config = picam2.create_preview_configuration() 

picam2.configure(camera_config) 
picam2.start_preview(Preview.QTGL) # Preview da imagem 

picam2.start()
time.sleep(10) # Tempo de aquisicao em segundos
picam2.capture_file(path)

print(f"Imagem salva em {path}")

# Resultado esperado: O código deve capturar uma imagem dois segundos após a inicialização da câmera (para permitir o foco) e salvará em um arquivo chamado "teste.jpg".
