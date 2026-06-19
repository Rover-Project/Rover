from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
import cv2 as openCv
from roverlib.modules.processing.processing_image import ProcessingImage

def circleVoting(hough, contorno):
    """Relaciona a detecção de dois metodos diferente"""
    
    if hough is None and contorno is None: # nada detectado
        return None

    if hough is None: # Somente um metodo detectou
        return contorno

    if contorno is None: # Somente um metodo detectou
        return hough

    x1, y1, r1 = hough
    x2, y2, r2 = contorno
    
    x1, y1, r1 = int(x1), int(y1), int(r1)
    x2, y2, r2 = int(x2), int(y2), int(r2)

    # votação:
    if abs(x1 - x2) < 20 and abs(y1 - y2) < 20:
        if abs(r1 - r2) < (r1 * 0.30):
            return ((x1 + x2)//2, (y1 + y2)//2, int((r1 + r2) / 2))

    # Se a discordancia for alta, retorna o metodo mais seguro
    return contorno
    
def inInterval(last, current, LIMIAR):
    # a e b são tuplas/listas (x, y, r)
    if current is None:
        return False
    for i in range(3):
        if abs(last[i] - current[i]) > LIMIAR:
            return False
    return True

def smoothDetect():
    HEIGHT = 640
    WIDTH = 640
    
    ESP32_IP = "192.168.4.1" 
    URL_STREAM = f"http://{ESP32_IP}:81/stream"

    # Inicializa a captura de vídeo apontando para a URL da ESP32
    camera = openCv.VideoCapture(URL_STREAM)

    camera.set(openCv.CAP_PROP_BUFFERSIZE, 1)
    camera.set(openCv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    camera.set(openCv.CAP_PROP_FRAME_HEIGHT, WIDTH)

    if not camera.isOpened():
        print("Erro: Não foi possível conectar ao stream. Verifique o IP ou se a ESP32 está ligada.")
        exit()

    circleHistory = None  # média acumulada
    cont = 0
    LIMIAR = 20  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 20  # número máximo de frames sem detecção
    noDetCounter = 0
    
    while True:
        _, frame = camera.read()
        
        if frame is not None:
            
            frame = openCv.resize(
                frame, 
                (HEIGHT, WIDTH),
                interpolation=openCv.INTER_CUBIC
            )

            mask = ProcessingImage.color_dual_segmentation(frame, gamma=1.9)
            hough, _ = VisionModule.houghCircleDetect(mask)
            contorno = VisionModule.circleCannyDetect(mask)

            # escolhe a melhor detecção entre hough e contorno
            if hough is not None and contorno is not None:
                det = circleVoting(hough, contorno)
            elif hough is not None:
                det = hough
            elif contorno is not None:
                det = contorno
            else:
                det = None

            if det is not None:
                noDetCounter = 0  # reset contador de frames sem detecção

                if circleHistory is None or not inInterval(det, circleHistory, LIMIAR):
                    circleHistory = list(det)  # converte tupla para lista
                    cont = 1
                else:
                    # acumula valores
                    circleHistory[0] += det[0]
                    circleHistory[1] += det[1]
                    circleHistory[2] += det[2]
                    cont += 1
            else:
                noDetCounter += 1
                # se muitos frames sem detecção, zera histórico
                if noDetCounter >= NO_DET_LIMIT:
                    circleHistory = None
                    cont = 0

            txt = "Nenhum circulo detectado"
            if circleHistory and cont > 0:
                # calcula média real
                x = circleHistory[0] // cont
                y = circleHistory[1] // cont
                r = circleHistory[2] // cont
                openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
                openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
                txt = f"X={x}  Y={y}  R={r}"

            openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            openCv.imshow("Deteccao Final", frame)
            openCv.imshow("Mascara", mask)

            if openCv.waitKey(1) & 0xFF == ord('q'):
                break

    camera.release()
    openCv.destroyAllWindows()
    
if __name__ == "__main__":
    smoothDetect()