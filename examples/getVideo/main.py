from roverlib.plugins.camera.camera import Camera
from pathlib import Path
import sys

try:
    file = sys.argv[1]
    duration = int(sys.argv[2])
except:
    print("Você não passou os parâmetros de linha de comando. file: caminho, duration: duração")

if __name__ == "__main__":
    
    home = Path.home()
    
    path = str(home / "Vídeos" / file) 
    
    camera = Camera(
        height=3840,
        width=2160,
        fps=30,
    ) 
    
    camera.start()
    # Configuração base de captura
    camera.set_brightness(0) 
    camera.set_contrast(1)
    camera.set_saturation(5)
    
    camera.get_video(file=path, t=duration)