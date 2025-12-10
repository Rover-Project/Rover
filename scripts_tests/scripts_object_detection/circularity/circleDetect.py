import cv2 as openCv
import numpy 
import math
from collections import deque
from picamera2 import Picamera2
import time

def gamma_correction(frame, gamma=1.9):
    """
        Manipula o brilho da imagem 
        gamma > 1: escurece os pixeis 
        gamma < 1: clareia os pixeis
    """

    # tabela de correção (0–255), faz uma nova quantização das cores
    table = numpy.array([
        ((i / 255.0) ** gamma) * 255
        for i in range(256)
    ]).astype("uint8")

    # Aplica a nova quantização aos pixels do frame
    corrected = openCv.LUT(frame, table)

    return corrected

def colorSegmentation(frame, low_color1=(0, 120, 70), upper_color1=(10, 255, 255), low_color2=(170, 120, 70), upper_color2=(180, 255, 255)):
    """
        Aplica mascaras com a cor passada pelos parametros(por padrão vemelhor), para realizar segmentação por cor.
    """
    
    # Converte a escala de por par HSV
    color_hsv = openCv.cvtColor(frame, openCv.COLOR_BGR2HSV)
    
    # Cria mascara com os cores passadas por parâmetro
    mask1 = openCv.inRange(color_hsv, numpy.array(low_color1), numpy.array(upper_color1))
    mask2 = openCv.inRange(color_hsv, numpy.array(low_color2), numpy.array(upper_color2))
    
    # Mecla as duas mascaras
    red_mask = openCv.bitwise_or(mask1, mask2)
    
    # limpa o ruido das mascaras
    red_mask = openCv.morphologyEx(red_mask, openCv.MORPH_OPEN, numpy.ones((5, 5), numpy.uint8))
    
    # Preenche buracos internos na mascara
    kernel_close = numpy.ones((15, 15), numpy.uint8)
    mask_close = openCv.morphologyEx(red_mask, openCv.MORPH_CLOSE, kernel_close)
    
    # preparando preenchimento de regioes por meio do floodfil
    fil = mask_close.copy()
    h, w = fil.shape[:2]
    
    # Mascara de preenchimento
    flood_mask = numpy.zeros((h + 2, w + 2), numpy.uint8)
    openCv.floodFill(fil, flood_mask, (0, 0), 255)
    fil_inv = openCv.bitwise_not(fil)
    
    # aplica floodfil na mascara
    mask_fil = mask_close | fil_inv # type: ignore
    
    # Borra imagem 
    mask_fil = openCv.GaussianBlur(mask_fil, (9, 9), 2)
    
    return mask_fil

def colorDualSegmentation(frame):
    """
        Realiza segmentação dupla para evitar "buracos" por causa da iluminação.
        Segmenta a imagem normal e depois uma imagem escurecida, no final mescla as duas.
    """
    
    frame = openCv.resize(frame, (640, 640))
    
    # Aplica filtro para escurecer a imagem
    dark = gamma_correction(frame, 2.3)

    mask_red_dark = colorSegmentation(dark) # Aplica segmentação por cor na mascara escurecida
    mask_red_normal = colorSegmentation(frame) # Aplica segmentação por cor na mascara normal
     
    # Mescla as duas mascaras
    mask_final = openCv.bitwise_or(mask_red_dark, mask_red_normal)

    # aplicar a máscara na imagem original
    segmented = openCv.bitwise_and(dark, dark, mask=mask_final)
    
    # Aplica canny na mascara final para pegar as bordas
    edges = openCv.Canny(mask_final, 50, 150)

    return mask_final, segmented, edges

def houghDetect(edges):
    """
        Transformada de hough mais completa ultilizando alguns filtros para aproximar ilipses de ciculos
    """
    
    # Cria uma mascara para formas elipticas
    kernel = openCv.getStructuringElement(openCv.MORPH_ELLIPSE, (7,7))
    
    # Aplica mascara eliptica para detectar bordas elipticas
    edges_ellipse = openCv.morphologyEx(edges, openCv.MORPH_CLOSE, kernel)

    circles = openCv.HoughCircles(
        edges_ellipse,
        openCv.HOUGH_GRADIENT,
        dp=1.3,
        minDist=50,
        param1=100,
        param2=40,
        minRadius=5,
        maxRadius=300
    )

    # Reconhece o maior ciculo
    if circles is not None:
        circles = numpy.uint16(numpy.around(circles[0]))
        circles = sorted(circles, key=lambda c: c[2], reverse=True) # type:ignore
        return tuple(circles[0]), edges_ellipse # retorna os dados do circulo e segmentação

    return None, edges_ellipse

def circleCannyDetect(mask, MINRADIUS=3, MINAREA=300):
    """Deteccao de circulos via contorno e coeficiente de circularidade, por meio das bordas"""
    
    # Aplica canny para reconhecimento de bordas
    edges = openCv.Canny(mask, 70, 150)
    contornos, _ = openCv.findContours(edges, openCv.RETR_EXTERNAL, openCv.CHAIN_APPROX_SIMPLE)

    # Ciculo com maior cicularidade detectado
    bestCircle = None
    bestScore = 999

    for cnt in contornos:
        area = openCv.contourArea(cnt)
        if area < MINAREA: # Descarta circulos muito pequenos
            continue

        # Detecta ciculos
        (x, y), r = openCv.minEnclosingCircle(cnt)
        r = int(r)

        if r <= MINRADIUS: # Descarta raios muito pequenos
            continue

        area_circ = math.pi * (r ** 2)
        erro = abs(area - area_circ) / area_circ

        # circularidade aceitável
        if erro < bestScore and erro < 0.35:
            bestScore = erro
            bestCircle = (int(x), int(y), r)

    return bestCircle

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
    """Suavia a deteccao de circulos"""
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (640, 640)})
    picam.configure(config)
    
    # Ajuste de exposição
    # picam.set_controls({
    #     "AnalogueGain": 1.5,   # controla amplificação do sensor, <1 = mais escuro
    #     "ExposureTime": 30000, # em microssegundos, menor = mais escuro
    # })
    # picam.start()

    circleHistory = None  # média acumulada
    cont = 0
    LIMIAR = 20  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 20  # número máximo de frames sem detecção
    noDetCounter = 0


    while True:
        frame = picam.capture_array()

        mask, _, _ = colorDualSegmentation(frame)
        hough, _ = houghDetect(mask)
        contorno = circleCannyDetect(mask)

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

    picam.stop()
    openCv.destroyAllWindows()

smoothDetect()