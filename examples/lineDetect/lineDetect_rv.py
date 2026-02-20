# Valores das variaveiz ajustados para o video5 
# Adicionar binarizacao como pre-processamento
# Adicionar mascara de cor como pre-processamento

from roverlib.modules.movement.robot import Robot
from roverlib.utils.config_manager import Config
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.camera.webcam import Webcam
from .lineMemory import memory
from .lineDecision import decision
import cv2 as openCV
import numpy
from pathlib import Path
HEIGHT = 640
WIDTH = 640

try:
    picam = Camera(HEIGHT, WIDTH) # Inicia a camera 
    picam.start()
except:
    #picam = Webcam(HEIGHT, WIDTH)
    pass

# Tecnica de binarizacao adptativa 
def binaryOtsu(img):
    
    otsu = openCV.THRESH_BINARY + openCV.THRESH_OTSU
    
    return openCV.threshold(
        img,
        0,
        255,
        otsu
    )

# Funcao que limita a area utilizada para desenho das linhas
def aplicar_roi(img):
    height, width = img.shape[:2]

    # Valor para retirar o capo dos carros 
    capo_offset = int(height * 0.9)

    # Definição do ROI(Region of Interest) (Ajustavel de acordo com a camera e ambiente)
    # Topo = Quanto maior o valor, mais baixo o Poligono
    bottom_left  = [width * 0, capo_offset]      # Canto inferior esquerdo 
    top_left     = [width * 0.2, height * 0.6] # Topo esquerdo 
    top_right    = [width * 0.65, height * 0.6] # Topo direito
    bottom_right = [width * 0.9, capo_offset]      # Canto inferior direito

    poligono = numpy.array([[bottom_left, top_left, top_right, bottom_right]], dtype=numpy.int32)

    # máscara preta
    mask = numpy.zeros_like(img)
    
    # Preenche o trapézio com branco
    openCV.fillPoly(mask, poligono, 255)

    # Aplica a máscara na imagem (mantém apenas o que está dentro do trapézio)
    mask_img = openCV.bitwise_and(img, mask)
    
    return mask_img

# Extrai as coordenadas a partir das linhas para desenho do poligono
def extrair_coordenadas_plano(lines, image_shape):
    left_pts = []
    right_pts = []
    
    if lines is None: return None

    for line in lines:
        coords = line.reshape(-1)
        if len(coords) >= 4:
            # Converte para int
            x1, y1, x2, y2 = map(int, coords[:4])
        else:
            continue

        # Cálculo da inclinação (m)
        # Se x2 - x1 for zero, a linha é vertical
        if abs(x2 - x1) < 0.005: 
            slope = 999 # Valor alto para representar verticalidade
        else:
            slope = (y2 - y1) / (x2 - x1)
 
        # linhas quase/ou horizontais (ruído, sombras, rachaduras).
        if abs(slope) < 0.7:
            print("Descartei") 
            continue

        parameters = numpy.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0] # inclinacao da reta
        intercept = parameters[1] 
        
        if slope < 0:
            left_pts.append((slope, intercept))
        else:
            right_pts.append((slope, intercept))

    # Tira a média de todas as linhas da esquerda e todas da direita
    left_avg = numpy.average(left_pts, axis=0) if left_pts else None
    right_avg = numpy.average(right_pts, axis=0) if right_pts else None
    
    return left_avg, right_avg

def obter_pontos_linha(y_min, y_max, line_parameters):
    if line_parameters is None: return None

    slope, intercept = line_parameters
    # x = (y - b) / m
    x_start = int((y_min - intercept) / slope)
    x_end = int((y_max - intercept) / slope)
    return [[x_start, y_min], [x_end, y_max]]

def lineDetectHough(img, isCut=False):
    height, width = img.shape[:2]
    
    if isCut:
        y_offset = int(height*0.6)
        workImage = img[y_offset, 0:width]
    else:
        y_offset = 0
        workImage = img

    # PRE-PROCESSAMENTO
    gray = openCV.cvtColor(workImage, openCV.COLOR_BGR2GRAY)
    blur = openCV.GaussianBlur(gray, (5, 5), 0)
    edges = openCV.Canny(blur, 50, 150)
    structElement = openCV.getStructuringElement(
        openCV.MORPH_RECT, 
        (3, 3)
    )
    edges = openCV.dilate(
        edges, 
        structElement, 
        iterations=1
    )
    roi = aplicar_roi(edges)

    # Detect linhas 
    lines = openCV.HoughLinesP(
        roi,
        rho=2,
        theta=numpy.pi / 180,
        threshold=60,
        minLineLength=65,
        maxLineGap=175
    )

    ajustadas = []

    # Desenha linhas 
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            declive = (x2 - x1)

            # Evita divisão por 0
            if declive < 0.1: 
                slope = 777
                # Vertical
            
            else: 
                slope = (y2 - y1) / declive

                if abs(slope) > 0.6:
                    ajustadas.append([[x1, y1 + y_offset, x2, y2 + y_offset]])
                    openCV.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return roi, img, numpy.array(ajustadas) if ajustadas else None

if __name__ == "__main__":
        # incializando    

        # Carrega configuração da gpio
        config = Config(Path(__file__).parent / "config.yaml")
    
        pins_motors = config.get("gpio")
        letf = (int(pins_motors["motor_esquerdo"]["in1"]), int(pins_motors["motor_esquerdo"]["in2"]))
        right = (int(pins_motors["motor_direito"]["in3"]), int(pins_motors["motor_direito"]["in4"]))
        
        # Inicia motores
        robot = Robot(left=letf, right=right)

        BASE_SPEED = 70
        KP = 0.4

        memoria = memory(frames_number=10)
        decisao = decision(BASE_SPEED)

        # *** LOOP ***
        while True:
            frame = picam.getFrame() # carrega frame

            frame = openCV.resize(
                frame, 
                (640, 640),
                interpolation=openCV.INTER_CUBIC
            )
            # 
            roi, frame_linhas, hough_data = lineDetectHough(frame)

            y_max = frame.shape[0]           # Base da imagem
            y_min = int(y_max * 0.6)         # Topo do ROI (variavel)
            
            frame_shape = frame.shape

            try:
                left_avg, right_avg = extrair_coordenadas_plano(hough_data, frame_shape)
                failure = False 
            except Exception as e:
                failure = True
                print("deu errado")
                
            if not failure:
                try:
                    left_avg = memoria.suavizar(left_avg, "left")
                    right_avg = memoria.suavizar(right_avg, "right")
                    ponto_esq = obter_pontos_linha(y_min, y_max, left_avg)
                    ponto_dir = obter_pontos_linha(y_min, y_max, right_avg)
                except Exception as e:
                    left_avg = memoria.suavizar(left_avg, "left")
                    right_avg = memoria.suavizar(right_avg, "right")
                    ponto_esq = []
                    ponto_dir = []
                    print(e)

                result = frame.copy() 

                if ponto_esq and ponto_dir:
                    # Desenho do plano verde
                    pts = numpy.array([ponto_esq[0], ponto_dir[0], ponto_dir[1], ponto_esq[1]], numpy.int32)
                    mask = numpy.zeros_like(frame)
                    openCV.fillPoly(mask, [pts], (0, 255, 0))
                    # Aplica o plano sobre o frame
                    result = openCV.addWeighted(frame, 1, mask, 0.4, 0)
                else:
                    print("Nao deu para detectar as faixas")

                # Sistema de Decisão
                direcao, erro = decisao.decide(frame, ponto_esq, ponto_dir)
                correcao = int(abs(erro) * KP)

                if direcao is "para":
                    robot.stop()
                    # implementar uma lógica que ele tenta identificar se é o final da pista ou
                    # Se ele saiu da pista
            
                else:
                    if erro > 0: 
                        left = min(100, BASE_SPEED - correcao)
                        right = max(0, BASE_SPEED + correcao)
                    elif erro < 0: 
                        left = max(0, BASE_SPEED + correcao)
                        right = min(100, BASE_SPEED - correcao)

                    robot.move(speed_left=left, speed_right=right)

                # Desenho do Painel de Log 
                overlay = result.copy()
                openCV.rectangle(overlay, (10, 10), (350, 130), (0, 0, 0), -1)
                result = openCV.addWeighted(overlay, 0.6, result, 0.4, 0) # Aplica transparência no painel

                # Inserção do texto do log
                openCV.putText(result, f"Status: {direcao}", (20, 40), 
                            openCV.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
                distancia = erro
                openCV.putText(result, f"{distancia:.1f} de erro", (20, 80), 
                            openCV.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

                cor_status = (0, 255, 0) if abs(erro) < 20 else (0, 0, 255)
                label_status = "LANE KEEPING: OK" if abs(erro) < 15 else "ALERTA: DESVIO"
                openCV.putText(result, label_status, (20, 110), 
                            openCV.FONT_HERSHEY_SIMPLEX, 0.5, cor_status, 2)

                # Desenho de um circulo para debug do centro da tela
                if ponto_esq and ponto_dir:
                    # O centro do frame(video5) esta levemente desalinhado com o do carro
                    calibragem_offset = 47
                    centro_cam = (frame.shape[1] / 2) 
                    centro_poligono = int((ponto_esq[1][0] + ponto_dir[1][0]) / 2) # centro poligono

                    openCV.circle(result, (centro_cam, y_max - 20), 10, (0, 0, 255), -1) # Desenha uma bola no centro em baixo da cam
                    openCV.circle(result, (centro_poligono, y_max - 20), 10, (255, 0, 0), -1) # desenha uma bola no centro da estrada

                # Exibicao das telas
                openCV.imshow("Navegacao Rover", result)
            openCV.imshow("ROI", roi)

            key = openCV.waitKey(25)
            
            if key == ord('q'):
                break
        openCV.destroyAllWindows()