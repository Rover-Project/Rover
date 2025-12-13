import cv2 as openCv
import numpy 
from ..processing.processing_image import ProcessingImage

class VisionModule:
    """
    Módulo responsável por processar frames da câmera e extrair informações
    para a navegação do Rover.
    """
    def __init__(self, resolution):
        """
        Inicializa o módulo de visão.
        Args:
            resolution (tuple): Resolução (largura, altura) dos frames de entrada.
        """
        self.width, self.height = resolution[0], resolution[1]
        print(f"Módulo de Visão inicializado. Resolução esperada: {self.width}x{self.height}")
        
    @classmethod
    def houghCircleDetect(cls, img, dp=1.3, minDist=50, canny=100, accumulation=40, minRadius=5, maxRadius=300):
        """
            Transformada de hough mais completa ultilizando alguns filtros para aproximar ilipses de ciculos
        """
        
        edges = ProcessingImage.edge_filter(img) # Aplica filtro de segmentacao de bordas
        
        # Cria uma mascara para formas elipticas
        kernel = openCv.getStructuringElement(openCv.MORPH_ELLIPSE, (7,7))
        
        # Aplica mascara eliptica para detectar bordas elipticas
        edges_ellipse = openCv.morphologyEx(edges, openCv.MORPH_CLOSE, kernel)

        circles = openCv.HoughCircles(
            edges_ellipse,
            openCv.HOUGH_GRADIENT,
            dp=dp,
            minDist=minDist,
            param1=canny,
            param2=accumulation,
            minRadius=minDist,
            maxRadius=maxRadius
        )

        # Reconhece o maior ciculo
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles[0]))
            circles = sorted(circles, key=lambda c: c[2], reverse=True) # type:ignore
            return tuple(circles[0]), edges_ellipse # retorna os dados do circulo e segmentação

        return None, edges_ellipse
    
    @classmethod
    def circleCannyDetect(cls, img, MINRADIUS=3, MINAREA=300, canny=(70, 150)):
        """Deteccao de circulos via contorno e coeficiente de circularidade, por meio das bordas"""
        
        # Aplica canny para reconhecimento de bordas
        edges = openCv.Canny(img, canny[0], canny[1])
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

            area_circ = numpy.pi * (r ** 2)
            erro = abs(area - area_circ) / area_circ

            # circularidade aceitável
            if erro < bestScore and erro < 0.35:
                bestScore = erro
                bestCircle = (int(x), int(y), r)

        return bestCircle
            

    def process_frame_for_line_following(self, frame):
        """
        Processa o frame para detectar uma linha e calcular o desvio do centro.

        Args:
            frame (numpy.array): Frame de entrada no formato BGR.

        Retorna:
            tuple: (desvio, frame_processado)
                desvio (float): Valor entre -1.0 (totalmente à esquerda) e 1.0 (totalmente à direita).
                                0.0 significa que a linha está centralizada.
                frame_processado (numpy.array): Frame com as marcações de processamento (opcional, para debug).
        """
        if frame is None:
            return 0.0, None

        # 1. Converter para HSV (Hue, Saturation, Value)
        hsv = openCv.cvtColor(frame, openCv.COLOR_BGR2HSV)

        # 2. Definir o intervalo de cor da linha (Exemplo: Linha Branca)
        lower_white = numpy.array([0, 0, 200])
        upper_white = numpy.array([180, 25, 255])
        mask = openCv.inRange(hsv, lower_white, upper_white)

        # 3. Aplicar uma região de interesse (ROI)
        roi_start_y = int(self.height * 0.8)
        mask[:roi_start_y, :] = 0
        
        # 4. Encontrar o centroide (Momento) da linha detectada
        M = openCv.moments(mask)

        desvio = 0.0
        cx = -1 # Coordenada X do centroide

        frame_processado = frame.copy()

        if M["m00"] > 0:
            # Calcular o centroide
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            openCv.circle(frame_processado, (cx, cy), 5, (0, 255, 0), -1)

            # 5. Calcular o desvio
            center_x = self.width / 2
            desvio = (cx - center_x) / center_x
        
        # Desenhar a linha central para referência
        openCv.line(frame_processado, (int(self.width/2), self.height), (int(self.width/2), roi_start_y), (255, 0, 0), 2)
        
        openCv.putText(frame_processado, f"Desvio: {desvio:.2f}", (10, 30), openCv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return desvio, frame_processado

    def detect_obstacle(self, frame, min_area_threshold=5000, color_range=None):
        """
        Detecta um obstáculo na frente do Rover com base na cor e tamanho.

        Args:
            frame (numpy.array): Frame de entrada no formato BGR.
            min_area_threshold (int): Área mínima (em pixels) para considerar um objeto como obstáculo.
            color_range (tuple, optional): Tupla (lower_hsv, upper_hsv) para a cor do obstáculo.
                                           Padrão: Vermelho (cor comum para cones ou barreiras).

        Retorna:
            tuple: (obstacle_detected, frame_processado)
                obstacle_detected (bool): True se um obstáculo for detectado.
                frame_processado (numpy.array): Frame com as marcações de detecção (para debug).
        """
        if frame is None:
            return False, None

        # Cor padrão: Vermelho (pode ser ajustado para o TCC)
        if color_range is None:
            # Vermelho tem dois intervalos em HSV
            lower_red1 = numpy.array([0, 100, 100])
            upper_red1 = numpy.array([10, 255, 255])
            lower_red2 = numpy.array([160, 100, 100])
            upper_red2 = numpy.array([180, 255, 255])
        else:
            lower_hsv, upper_hsv = color_range
            lower_red1 = lower_hsv
            upper_red1 = upper_hsv
            lower_red2 = numpy.array([0, 0, 0]) # Ignora o segundo intervalo se um range específico for fornecido
            upper_red2 = numpy.array([0, 0, 0])

        hsv = openCv.cvtColor(frame, openCv.COLOR_BGR2HSV)

        # Cria as máscaras para os dois intervalos de vermelho
        mask1 = openCv.inRange(hsv, lower_red1, upper_red1)
        mask2 = openCv.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        # Aplica operações morfológicas para remover ruído
        mask = openCv.erode(mask, None, iterations=2)
        mask = openCv.dilate(mask, None, iterations=2)

        # Encontra contornos na máscara
        contours, _ = openCv.findContours(mask.copy(), openCv.RETR_EXTERNAL, openCv.CHAIN_APPROX_SIMPLE)

        obstacle_detected = False
        frame_processado = frame.copy()

        if len(contours) > 0:
            # Encontra o maior contorno (assumindo que o obstáculo é o maior objeto)
            c = max(contours, key=openCv.contourArea)
            area = openCv.contourArea(c)

            if area > min_area_threshold:
                obstacle_detected = True
                # Desenha o contorno e o retângulo delimitador no frame de debug
                x, y, w, h = openCv.boundingRect(c)
                openCv.rectangle(frame_processado, (x, y), (x + w, y + h), (0, 0, 255), 2)
                openCv.putText(frame_processado, "OBSTACULO", (x, y - 10), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                openCv.putText(frame_processado, f"Area: {area}", (x, y + h + 20), openCv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        openCv.putText(frame_processado, f"Obstaculo: {obstacle_detected}", (10, 60), openCv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return obstacle_detected, frame_processado

# exemplo de uso (para testes)
if __name__ == "__main__":
    
    test_width, test_height = 640, 480
    test_frame = numpy.zeros((test_height, test_width, 3), dtype=numpy.uint8)
    
    
    openCv.rectangle(test_frame, (250, 200), (400, 350), (0, 0, 255), -1) # desenha um quadrado vermelho no centro
    
    vision = VisionModule((test_width, test_height))
    
    # Teste de detecção de linha (apenas para garantir que a função anterior ainda funciona)
    desvio, processed_line_frame = vision.process_frame_for_line_following(test_frame)
    print(f"Desvio de linha (com obstáculo): {desvio}")
    
    # Teste de detecção de obstáculo
    obstacle_detected, processed_obstacle_frame = vision.detect_obstacle(test_frame, min_area_threshold=1000)
    
    print(f"Obstáculo detectado: {obstacle_detected}")
    
    
    if processed_obstacle_frame is not None:    # salva o frame processado para visualização
        openCv.imwrite("test_obstacle_frame.jpg", processed_obstacle_frame)
        print("Frame de teste de obstáculo salvo como 'test_obstacle_frame.jpg'")
    else:
        print("Falha no processamento do frame de teste de obstáculo.")
