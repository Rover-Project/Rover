import cv2
import numpy as np
import math
from collections import deque
from picamera2 import Picamera2
import time

ultimo = None          # último círculo detectado
consistencia = 0       # contagem de consistência
LIMIAR_FRAMES = 5      # número mínimo de frames consistentes

def suaviza(frame):
    """Filtro para tentar suvizar o brilho"""
    
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l2 = clahe.apply(l)

    lab = cv2.merge((l2, a, b))
    frame_clahe = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    smooth = cv2.bilateralFilter(frame_clahe, 9, 75, 75)
    
    return smooth

def darken_hsv(frame, factor=0.6):
    """Diminui o brilho da imagem usando o canal de brilho da imagem"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # separar canais
    h, s, v = cv2.split(hsv)

    # reduzir iluminação
    v = np.clip(v.astype(np.float32) * factor, 0, 255).astype(np.uint8)

    # juntar canais de volta
    hsv_dark = cv2.merge([h, s, v])

    # voltar para BGR
    darker = cv2.cvtColor(hsv_dark, cv2.COLOR_HSV2BGR)

    return darker

def gamma_correction(frame, gamma=1.9):
    """Escurece imagem"""
    
    # evita divisão por zero
    inv_gamma = gamma

    # tabela de correção (0–255)
    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in range(256)
    ]).astype("uint8")

    # aplica transformação
    corrected = cv2.LUT(frame, table)

    return corrected

def redSegmentation(frame):
    """Aplica mascaras vemelhas para realizar uma segmentacao de objetos vermelhos"""
    
    # limites HSV da cor vermelha
    lower_red1 = (0, 120, 70)
    upper_red1 = (10, 255, 255)

    lower_red2 = (170, 120, 70)
    upper_red2 = (180, 255, 255)
    
    frame = cv2.resize(frame, (640, 640))
    
    color_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    
    mask1 = cv2.inRange(color_hsv, np.array(lower_red1), np.array(upper_red1))
    mask2 = cv2.inRange(color_hsv, np.array(lower_red2), np.array(upper_red2))
    
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    
    # Preenche buracos internos na segmentacao
    kernel_close = np.ones((15, 15), np.uint8)
    mask_close = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel_close)
    
    fil = mask_close.copy()
    h, w = fil.shape[:2]
    
    flood_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(fil, flood_mask, (0, 0), 255)
    fil_inv = cv2.bitwise_not(fil)
    
    mask_fil = mask_close | fil_inv # type: ignore
    
    mask_fil = cv2.GaussianBlur(mask_fil, (9, 9), 2)
    
    return mask_fil

def redSegmentationDuble(frame):
    """Segmenta um frame em duas partes segmentando a parte mais brilhosa e a parte mais escura"""
    frame = cv2.resize(frame, (640, 640))
    
    dark = gamma_correction(frame, 2.3)

    mask_red_dark = redSegmentation(dark)
    mask_red_normal = redSegmentation(frame)
     
    mask_final = cv2.bitwise_or(mask_red_dark, mask_red_normal)

    # aplicar a máscara na imagem original
    segmented = cv2.bitwise_and(dark, dark, mask=mask_final)
    
    edges = cv2.Canny(mask_final, 50, 150)

    return mask_final, segmented, edges

def mascara_vermelha(frame):
    """Mascara vemelha simples sem aplicacao de filtros para tratamento do brilho"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # duas faixas do vermelho
    lower1 = np.array([0, 120, 70])
    upper1 = np.array([10, 255, 255])

    lower2 = np.array([170, 120, 70])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)

    # limpeza da máscara
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def detectar_hough(mask):
    """Tranformada de hough padrao"""

    # parâmetros fixos escolhidos como bons padrões gerais
    dp = 1.2
    minDist = 50
    param1 = 150
    param2 = 22
    minRadius = 10
    maxRadius = 200

    circles = cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=minDist,
        param1=param1,
        param2=param2,
        minRadius=minRadius,
        maxRadius=maxRadius
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = sorted(circles[0], key=lambda c: c[2], reverse=True)
        return tuple(circles[0])  # (x, y, r)

    return None

def hough_robusto(edges):
    """Transformada de hough mais complexa ultilizando alguns filtros para aproximar ilipses de ciculos"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    edges2 = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    circles = cv2.HoughCircles(
        edges2,
        cv2.HOUGH_GRADIENT,
        dp=1.3,
        minDist=50,
        param1=100,
        param2=40,
        minRadius=5,
        maxRadius=300
    )

    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        circles = sorted(circles, key=lambda c: c[2], reverse=True)
        return tuple(circles[0]), edges2

    return None, edges2

def detectar_contorno(mask):
    """Deteccao de circulos via contorno e coeficiente de circularidade"""
    edges = cv2.Canny(mask, 70, 150)
    contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    melhor = None
    melhor_score = 999

    for cnt in contornos:
        area = cv2.contourArea(cnt)
        if area < 300:
            continue

        (x, y), r = cv2.minEnclosingCircle(cnt)
        r = int(r)

        if r <= 3:
            continue

        area_circ = math.pi * (r ** 2)
        erro = abs(area - area_circ) / area_circ

        # circularidade aceitável
        if erro < melhor_score and erro < 0.35:
            melhor_score = erro
            melhor = (int(x), int(y), r)

    return melhor

def combinar(hough, contorno):
    """Conbinas os dois dados de deteccao de ciculos"""
    if hough is None and contorno is None:
        return None

    if hough is None:
        return contorno

    if contorno is None:
        return hough

    x1, y1, r1 = hough
    x2, y2, r2 = contorno

    # se concordarem:
    if abs(x1 - x2) < 20 and abs(y1 - y2) < 20:
        if abs(r1 - r2) < (r1 * 0.30):
            return ((x1 + x2)//2, (y1 + y2)//2, int((r1 + r2) / 2))

    # se discordarem totalmente: confie mais no contorno
    return contorno

# valores globais para filtro temporal
filtro_x = filtro_y = filtro_r = None
ALPHA = 0.4  # quanto maior, mais rápido o filtro segue a bola

# filtro exponencial global
filtro_x = filtro_y = filtro_r = None
ALPHA = 0.4  # suavidade do movimento (0=mais lento, 1=mais rápido)

HISTORY_LENGTH = 5
hough_history = deque(maxlen=HISTORY_LENGTH)
contorno_history = deque(maxlen=HISTORY_LENGTH)

def combinar_estavel(hough_history, contorno_history):
    """Conbina, mas com uma suavizacao"""
    global filtro_x, filtro_y, filtro_r

    # média das últimas detecções (Hough + Contorno)
    valores = []
    if len(hough_history) > 0:
        valores.append(np.mean(hough_history, axis=0))
    if len(contorno_history) > 0:
        valores.append(np.mean(contorno_history, axis=0))
    if not valores:
        return None

    x_new, y_new, r_new = np.mean(valores, axis=0)

    # aplica filtro exponencial para suavizar
    if filtro_x is None:
        filtro_x, filtro_y, filtro_r = x_new, y_new, r_new
    else:
        filtro_x = ALPHA * x_new + (1 - ALPHA) * filtro_x
        filtro_y = ALPHA * y_new + (1 - ALPHA) * filtro_y
        filtro_r = ALPHA * r_new + (1 - ALPHA) * filtro_r

    return int(filtro_x), int(filtro_y), int(filtro_r)


def filtro_temporal(circ):
    """Faz a analise dos ultimos 5 frames se tiver uma cicuferencena ele aceita"""
    global ultimo, consistencia

    if circ is None:
        ultimo = None
        consistencia = 0
        return None

    if ultimo is None:
        ultimo = circ
        consistencia = 1
        return None

    x, y, r = circ
    ux, uy, ur = ultimo

    # diferenças entre frames
    if abs(x - ux) < 25 and abs(y - uy) < 25 and abs(r - ur) < (ur * 0.25):
        consistencia += 1
    else:
        consistencia = 0

    ultimo = circ

    # só aceita depois de N frames estáveis
    if consistencia >= LIMIAR_FRAMES:
        return circ

    return None

def folowCircle():
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (640, 640)})
    picam.configure(config)
    picam.start()

    while True:
        time.sleep(0.3)
        frame = picam.capture_array()

        #frame = cv2.resize(frame, (640, 640))

        # máscara da bola (usar sua função de segmentação)
        mask, _, _ = redSegmentationDuble(frame)

        # detectar círculo Hough e Contorno
        hough, _ = hough_robusto(mask)
        contorno = detectar_contorno(mask)

        # atualizar históricos
        if hough:
            hough_history.append(hough)
        if contorno:
            contorno_history.append(contorno)

        # combina de forma estável e suavizada
        combinado = combinar_estavel(hough_history, contorno_history)

        txt = "Nenhum círculo detectado"
        if combinado:
            x, y, r = combinado
            cv2.circle(frame, (x, y), r, (0, 255, 0), 3)
            cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
            txt = f"X={x}  Y={y}  R={r}"

        cv2.putText(frame, txt, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Deteccao Final (Estável)", frame)
        cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    cv2.destroyAllWindows()
    
def inInterval(a, b, l):
    # a e b são tuplas/listas (x, y, r)
    if b is None:
        return False
    for i in range(3):
        if abs(a[i] - b[i]) > l:
            return False
    return True

def avCircle():
    """Suavia a deteccao de circulos"""
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (640, 640)})
    picam.configure(config)
    picam.start()

    circleHistory = None  # média acumulada
    cont = 0
    LIMIAR = 20  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 30  # número máximo de frames sem detecção
    noDetCounter = 0
    
    cv2.namedWindow("Deteccao Final (Estável)", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Mascara", cv2.WINDOW_NORMAL)


    while True:
        time.sleep(0.3)
        frame = picam.capture_array()

        #frame = cv2.resize(frame, (640, 640))

        mask, _, _ = redSegmentationDuble(frame)
        hough, _ = hough_robusto(mask)
        contorno = detectar_contorno(mask)

        # escolhe a melhor detecção entre hough e contorno
        if hough is not None and contorno is not None:
            det = combinar(hough, contorno)
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

        txt = "Nenhum círculo detectado"
        if circleHistory and cont > 0:
            # calcula média real
            x = circleHistory[0] // cont
            y = circleHistory[1] // cont
            r = circleHistory[2] // cont
            cv2.circle(frame, (x, y), r, (0, 255, 0), 3)
            cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
            txt = f"X={x}  Y={y}  R={r}"

        #cv2.putText(frame, txt, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Deteccao Final (Estável)", frame)
        cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    cv2.destroyAllWindows()

avCircle()