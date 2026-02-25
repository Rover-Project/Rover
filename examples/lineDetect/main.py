from roverlib.plugins.camera.camera import Camera # type: ignore
from .lineMemory import memory
from .lineDecision import decision
import cv2 as openCV # type: ignore
from pathlib import Path
import numpy # type: ignore
import math

HEIGHT = 640 # Altura da camera
WIDTH = 640 # Comprimento da camera
start = False # Flag para controlar o inicio do movimento do Rover
drive_mode = None # Flag para controlar o modelo de pista que o Rover deve esperar

try:
    picam = Camera(HEIGHT, WIDTH,verticalFlip=True) # Inicia a camera 
    picam.start()
except:
    #picam = Webcam(HEIGHT, WIDTH)
    pass

# Funcao que limita a area utilizada para desenho das linhas
def roi_definition(img):
    height, width = img.shape[:2]

    # Definição do ROI(Region of Interest) (Ajustavel de acordo com a camera e ambiente)
    # Topo = Quanto maior o valor, mais baixo o Poligono
    bottom_left  = [width * 0.9, height]      # Canto inferior esquerdo 
    top_left     = [width * 0.65, height * 0.6] # Topo esquerdo 
    top_right    = [width * 0.65, height * 0.6] # Topo direito
    bottom_right = [width * 0.9, height]      # Canto inferior direito

    # Forma o poligono de acordo com as medidas do ROI
    poligono = numpy.array([[bottom_left, top_left, top_right, bottom_right]], dtype=numpy.int32)

    # máscara preta
    mask = numpy.zeros_like(img)
    
    # Preenche o trapézio com branco
    openCV.fillPoly(mask, poligono, 255)

    # Aplica a máscara na imagem (mantém apenas o que está dentro do trapézio)
    mask_img = openCV.bitwise_and(img, mask)
    
    return mask_img

# Extrai as coordenadas a partir das linhas para desenho do poligono (Regiao dirigivel dentro do ROI)
def extract_coords(lines, drive_mode: str, image_shape):
    # lists para os pontos das linhas na esquerda e direita
    left_pts = []
    right_pts = []
    line_pts = []

    if lines is None or not drive_mode: return None

    for line in lines:

        # Muda as dimensoes do array de forma automatica (param -> -1)
        coords = line.reshape(-1)
        if len(coords) >= 4:
            # Converte para int
            x1, y1, x2, y2 = map(int, coords[:4])
        else:
            continue

        dx = x2 - x1
        dy = y2 - y1

        # Cálculo da inclinação
        rad_angle = math.atan2(dy, dx)
        degree_angle = math.degrees(rad_angle)

        abs_angle = abs(degree_angle)

        # linhas quase/ou horizontais (ruído, sombras, rachaduras).
        if 30 > abs_angle or abs_angle > 160:
            print("Descartei") 
            continue
        
        parameters = numpy.polyfit((x1, x2), (y1, y2), 1) # retorna n + 1 coeficientes para um angulo n (1 nesse caso) polinomial
        slope = parameters[0] # inclinacao da reta
        intercept = parameters[1]  # Onde a linha toca o eixo x(Ajuda separar linha da esquerda da linha da direita)

        if drive_mode == 'road':
            if slope < 0:
                left_pts.append((slope, intercept))
            else:
                right_pts.append((slope, intercept))

            # Tira a média de todas as linhas da esquerda e todas da direita
            left_avg = numpy.average(left_pts, axis=0) if left_pts else None
            right_avg = numpy.average(right_pts, axis=0) if right_pts else None
            
            return left_avg, right_avg
    
        else:
            line_pts.append((slope, intercept))
            line_avg = numpy.average(line_pts, axis=0) if line_pts else None
            return line_avg
        
def cat_x_linepoints(y_min, y_max, line_parameters):
    if line_parameters is None: return None

    slope, intercept = line_parameters
    # apartir de y = mx + b ==>  x = (y - b) / m
    try:
        # Calcula onde linhas distantes(picotadas) tocam o eixo x
        # Suavizando o desenho delas
        x_start = int((y_min - intercept) / slope)
        x_end = int((y_max - intercept) / slope)
        return [[x_start, y_min], [x_end, y_max]] # 
    
    except Exception as e:
        print(f'error: {e}')

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
    roi = roi_definition(edges)

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

            rad_angle = math.atan2(dy, dx)
            degree_angle = math.degrees(rad_angle)

            abs_angle = abs(degree_angle)
            if 30 < abs_angle < 160:    

                ajustadas.append([[x1, y1 + y_offset, x2, y2 + y_offset]])
                openCV.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return roi, img, numpy.array(ajustadas) if ajustadas else None

if __name__ == "__main__":
        # incializando    
        memoria = memory(frames_number=10)
        decisao = decision()

        # *** LOOP ***
        while True:
            frame = picam.get_frame() # carrega frame

            # --- INICIALIZAÇÃO DE FALLBACK ---
            left_avg = None # Media das linhas a esquerda (road mode)
            right_avg = None # Media das linhas a direita (road mode)
            right_point = None # Pontos a direita pro desenho da região dirigivel
            left_point = None # Pontos a esquerda pro desenho da região dirigivel
            target_line = None # Linha que o Rover deve se manter (line mode)
            result = frame.copy()  # Garante que 'result' sempre exista
            all_points = None # futura tupla pra guardar right e left points
            line_points = None # guarda os pontos da linha
            direcao, erro = "Aguardando", 0 # Define uma direção e valor de erro padrão 
            # --------------------------------

            # retorna o ROI, frame com as linhas desenhadas e os dados das linhas encontradas
            roi, frame_linhas, hough_data = lineDetectHough(frame)

            y_max = frame.shape[0]           # Base da imagem
            y_min = int(y_max * 0.6)         # Topo do ROI (variavel)
            
            frame_shape = frame.shape

            key = openCV.waitKey(10) & 0xFF
            
            # Requisita que seja dado o start e que um type seja selecionado
            # Apertar 's' e depois 'r' ou 'l'
                # start --- começa o programa
            if key == ord('s'):
                start = True
                print("Rover has been started")

            # change --- Define type para None, permitindo a troca de modo de pista
            if key == ord('c') and start:
                drive_mode = None
                start = False
                print("drive mode resetado")

            # road --- road mode
            if key == ord('r') and start:
                drive_mode = 'road'
                print("drive mode = road")

            # line --- line mode
            if key == ord('l') and start:
                drive_mode = 'line'
                print("drive mode = line")

            # Saiu do loop de selecao de modo, verifica qual type foi escolhido e executa o script apartir disso

            # TYPE == ROAD
            if drive_mode == 'road':

                # Tenta pegar a posicao media das linhas a partir da hough_data
                try:
                    left_avg, right_avg = extract_coords(hough_data, frame_shape)
                    error = False 
                except Exception as e:
                    error = True
                    result = frame # Garante que result(um dos frames exibidos pelo opencv) chega no fim do script
                    print(f"Não foi possível extrair as coordenadas das linhas {e}")
                    
                if not error:
                    try:
                        # utiliza da memoria para prover mais precisao nos pontos
                        left_avg = memoria.suavizar(left_avg, "left") 
                        right_avg = memoria.suavizar(right_avg, "right")

                        # usa funcao da reta reorganizada nao depender do que o Rover ve logo a sua frente, apenas
                        left_point = cat_x_linepoints(y_min, y_max, left_avg)
                        right_point = cat_x_linepoints(y_min, y_max, right_avg)
                        all_points = (left_point, right_point)
                    except Exception as e:
                        left_avg = memoria.suavizar(left_avg, "left")
                        right_avg = memoria.suavizar(right_avg, "right")
                        left_point = []
                        right_point = []
                        print(f"Não foi possível definir line_points {e}")

                    result = frame.copy() 

                    if left_point and right_point:
                        # Desenho do plano verde
                        pts = numpy.array([left_point[0], right_point[0], right_point[1], left_point[1]], numpy.int32)
                        mask = numpy.zeros_like(frame)
                        openCV.fillPoly(mask, [pts], (0, 255, 0))

                        # Aplica o plano sobre o frame
                        result = openCV.addWeighted(frame, 1, mask, 0.4, 0)
                    else:
                        print("Nao deu para detectar as faixas")
                        result = frame
            
            if drive_mode == 'line':
                try:
                    line_avg = extract_coords(hough_data, drive_mode, frame_shape)
                    error = False
                
                except Exception as e:
                    error = True
                    print(f"Não foi possível extrair as coordenadas das linhas {e}")
                
                if not error:
                    try: 
                        line_points = cat_x_linepoints(y_min, y_max, line_avg)
                    
                    except Exception as e:
                        line_points = None
                        print(f"Não foi possível definir line_points {e}")

                else:
                    print("Não foi possível detectar a linha")

            # decisão do Rover
            direcao, erro = decisao.decide(frame, all_points, target_line, drive_mode)

            # Desenho do Painel de Log 
            overlay = result.copy()
            openCV.rectangle(overlay, (10, 10), (350, 130), (0, 0, 0), -1)
            result = openCV.addWeighted(overlay, 0.6, result, 0.4, 0) # Aplica transparência no painel

            # Inserção do texto do log
            openCV.putText(result, f"Status: {direcao}", (20, 40), 
                        openCV.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
            openCV.putText(result, f"{erro:.1f} de erro", (20, 80), 
                        openCV.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            cor_status = (0, 255, 0) if abs(erro) < 20 else (0, 0, 255)
            label_status = "LANE KEEPING: OK" if abs(erro) < 15 else "ALERTA: DESVIO"
            openCV.putText(result, label_status, (20, 110), 
                        openCV.FONT_HERSHEY_SIMPLEX, 0.5, cor_status, 2)

            # Desenho de um circulo para debug do centro da tela
            if left_point and right_point or line_points:
            
                centro_cam = (frame.shape[1] / 2)
                centro_poligono = int((left_point[1][0] + right_point[1][0]) / 2 if not line_points else line_points[1][0]) # centro poligo

                openCV.circle(result, (centro_cam, y_max - 20), 10, (0, 0, 255), -1) # Desenha uma bola no centro em baixo da cam
                openCV.circle(result, (centro_poligono, y_max - 20), 10, (255, 0, 0), -1) # desenha uma bola no centro da estrada

                # Exibicao das telas
            openCV.imshow("Navegacao Rover", result)
            openCV.imshow("ROI", roi)
            
            # --- ADICIONE ESTA PARTE AQUI ---
            # Verifica se a tecla 'q' foi pressionada para sair do loop principal
            if openCV.waitKey(1) & 0xFF == ord('q'):
                break

        openCV.destroyAllWindows()