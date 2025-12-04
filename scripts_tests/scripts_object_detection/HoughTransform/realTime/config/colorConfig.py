from picamera2 import Picamera2
import cv2 as openCv
import time
from saveJson import saveConfig

def colorDetect(nameColor: str, h=680, w=480, limiar=5):
    picam = Picamera2()

    config = picam.create_preview_configuration(
        main=
        {
            "format": "RGB888", 
            "size": (h, w)
        }
    )
    
    picam.configure(config)
    picam.start()
    time.sleep(1)

    while True:
        frame = picam.capture_array()

        hsv = openCv.cvtColor(frame, openCv.COLOR_RGB2HSV)

        # Pixel central
        cx, cy = w // 2, h // 2
        hsv_center = hsv[cy, cx]
        
        # extraindo valores hsv
        color = {
            "low": {
                "hue": hsv_center[0] - limiar, 
                "saturation": hsv_center[1] - limiar, 
                "value": hsv_center[2] - limiar
            },
            "high": {
                "hue": hsv_center[0] + limiar, 
                "saturation": hsv_center[1] + limiar, 
                "value": hsv_center[2] + limiar
            }
        }

        print("HSV centro:", hsv_center)

        # Mostrar um quadradinho no centro
        openCv.rectangle(frame, (cx - 10, cy - 10), (cx + 10, cy + 10), (0, 255, 0), 1)

        openCv.imshow("Imagem Original", frame)
        
        key = (openCv.waitKey(1) & 0xFF)
        
        if key == ord('s'):
            saveConfig(color, nameColor)

        if key & 0xFF == ord('q'):
            break

    picam.stop()
    openCv.destroyAllWindows()

if __name__ == "__main__":
    
    nameFile = input("Digite o nome do arquivo: ")
    colorDetect(nameColor=nameFile)
