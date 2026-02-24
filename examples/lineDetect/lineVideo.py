# Valores das variaveiz ajustados para o video5 
# Adicionar binarizacao como pre-processamento
# Adicionar mascara de cor como pre-processamento

# Adiciona a pasta 'Rover' principal ao caminho de busc
from roverlib.plugins.camera.camera import Camera
from .lineMemory import memory
from .lineDecision import decision
import cv2 as openCV
from pathlib import Path
import numpy
import math

HEIGHT = 640
WIDTH = 640
start = False
type = None

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
        dx = x2 - x1
        dy = y2 - y1

        # Cálculo da inclinação
        rad_angle = math.atan(dx, dy)
        degree_angle = math.degrees(rad_angle)

        abs_angle = degree_angle

        # linhas quase/ou horizontais (ruído, sombras, rachaduras).
        if 30 > abs_angle or abs_angle > 160:
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

            dx = x2 - x1
            dy = y2 - y1

            rad_angle = math.atan(dy, dx)
            degree_angle = math.degrees(rad_angle)

            abs_angle = abs(degree_angle)
            if 30 < abs_angle < 160:    

                ajustadas.append([[x1, y1 + y_offset, x2, y2 + y_offset]])
                openCV.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return roi, img, numpy.array(ajustadas) if ajustadas else None

if __name__ == "__main__":
        # incializando    
        memoria = memory(frames_number=10)
        decisao = decision(HEIGHT, WIDTH)

        # *** LOOP ***
        while True:
            frame = picam.get_frame() # carrega frame

            roi, frame_linhas, hough_data = lineDetectHough(frame)

            y_max = frame.shape[0]           # Base da imagem
            y_min = int(y_max * 0.6)         # Topo do ROI (variavel)
            
            frame_shape = frame.shape

            try:
                left_avg, right_avg = extrair_coordenadas_plano(hough_data, frame_shape)
                error = False 
            except Exception as e:
                error = True
                print("deu errado")
                
            if not error:
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

                key = openCV.waitKey(10) & 0xFF

                if key == ord('q'):
                    break
                
                if key == ord('i'):
                    start = True

                if key == ord('r') and start:
                    type = 'road'

                if key == ord('l') and start:
                    type = 'line'

                # Sistema de Decisão
                direcao, erro = decisao.decide(frame, ponto_esq, ponto_dir)

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
                
                    centro_cam = (frame.shape[1] / 2) 
                    centro_poligono = int((ponto_esq[1][0] + ponto_dir[1][0]) / 2) # centro poligono

                    openCV.circle(result, (centro_cam, y_max - 20), 10, (0, 0, 255), -1) # Desenha uma bola no centro em baixo da cam
                    openCV.circle(result, (centro_poligono, y_max - 20), 10, (255, 0, 0), -1) # desenha uma bola no centro da estrada

                # Exibicao das telas
                openCV.imshow("Navegacao Rover", result)
            openCV.imshow("ROI", roi)
                # log_file.write(f"{time.time()},{direcao},{erro}\n")

            key = openCV.waitKey(25)
            
            
        openCV.destroyAllWindows()