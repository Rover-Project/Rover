import cv2 as openCv
import numpy 
from roverlib.modules.processing.processing_image import ProcessingImage

class VisionModule:
    """
    Detecção de formas e objetos em imagens: círculos, linha a seguir e obstáculos coloridos.

    `houghCircleDetect()` e `circleCannyDetect()` são métodos de classe (use sem criar objeto) e
    recebem uma **máscara** (por exemplo, de `ProcessingImage.color_segmentation()`).
    `process_frame_for_line_following()` e `detect_obstacle()` precisam de um objeto criado com a
    resolução dos frames.

    Exemplo:

    ```python
    mascara = ProcessingImage.color_segmentation(frame)
    circulo, _ = VisionModule.houghCircleDetect(mascara)
    if circulo is not None:
        x, y, raio = circulo
    ```
    """
    def __init__(self, resolution):
        """
        Args:
            resolution (tuple): `(largura, altura)` dos frames que serão processados.
        """
        self.width, self.height = resolution[0], resolution[1]
        print(f"Módulo de Visão inicializado. Resolução esperada: {self.width}x{self.height}")
        
    @classmethod
    def houghCircleDetect(cls, img, dp=1.3, minDist=50, canny=100, accumulation=40, minRadius=5, maxRadius=300):
        """
        Detecta o círculo mais evidente em uma máscara usando a Transformada de Hough.

        Antes do Hough, as bordas da máscara são extraídas (Canny) e fechadas com um filtro
        elíptico, o que ajuda a reconhecer objetos redondos vistos um pouco de lado.

        Args:
            img (numpy.ndarray): máscara binária (branco = objeto).
            dp (float): resolução do acumulador do Hough (1 = resolução da imagem). Padrão 1.3.
            minDist (int): distância mínima entre centros de círculos, em pixels. Padrão 50.
            canny (int): limiar superior do Canny interno do Hough. Padrão 100.
            accumulation (int): votos necessários para aceitar um círculo; menor encontra mais
                círculos, inclusive falsos. Padrão 40.
            minRadius (int): menor raio procurado, em pixels. Padrão 5.
            maxRadius (int): maior raio procurado, em pixels. Padrão 300.

        Returns:
            tuple: `(circulo, bordas)`. `circulo` é `(x, y, raio)` em pixels (inteiros) do círculo
                mais votado, ou None se nenhum for encontrado; `bordas` é a imagem de bordas usada.
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
            minRadius=minRadius,
            maxRadius=maxRadius
        )

        # O OpenCV ordena os círculos pelo número de votos: o primeiro é o mais confiável.
        # (Escolher o de maior raio pegava círculos falsos, maiores que o objeto.)
        if circles is not None:
            # int comum (e não uint16) para não estourar em subtrações feitas pelo usuário
            best = numpy.around(circles[0][0]).astype(int)
            return tuple(int(v) for v in best), edges_ellipse # retorna os dados do circulo e segmentação

        return None, edges_ellipse
    
    @classmethod
    def circleCannyDetect(cls, img, MINRADIUS=3, MINAREA=300, canny=(70, 150)):
        """
        Detecta o contorno mais redondo de uma máscara.

        Para cada contorno, compara a área real com a do círculo que o envolve: quanto mais
        parecidas, mais redondo é o objeto. Complementa o `houghCircleDetect()` (os exemplos
        combinam os dois por votação).

        Args:
            img (numpy.ndarray): máscara binária (branco = objeto).
            MINRADIUS (int): raio mínimo aceito, em pixels. Padrão 3.
            MINAREA (int): área mínima do contorno, em pixels². Padrão 300.
            canny (tuple): limiares `(inferior, superior)` do filtro de Canny. Padrão `(70, 150)`.

        Returns:
            tuple | None: `(x, y, raio)` em pixels do contorno mais circular (erro de área abaixo
                de 35%), ou None.
        """
        
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
        Calcula o desvio de uma linha **branca** em relação ao centro da imagem.

        Só a faixa inferior da imagem (20% de baixo, logo à frente do Rover) é analisada.

        Args:
            frame (numpy.ndarray): imagem em BGR.

        Returns:
            tuple: `(desvio, frame_processado)`. `desvio` vai de -1.0 (linha toda à esquerda)
                a 1.0 (toda à direita); 0.0 significa linha centralizada ou não encontrada.
                `frame_processado` é uma cópia com as marcações, para visualização.
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
        Detecta um objeto colorido grande o bastante para ser considerado um obstáculo.

        Args:
            frame (numpy.ndarray): imagem em BGR.
            min_area_threshold (int): área mínima do objeto, em pixels, para contar como obstáculo. Padrão 5000.
            color_range (tuple, optional): `(hsv_inferior, hsv_superior)` da cor procurada.
                Padrão: vermelho.

        Returns:
            tuple: `(detectado, frame_processado)`. `detectado` é True se houver obstáculo;
                `frame_processado` é uma cópia com o objeto marcado, para visualização.
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
        mask = openCv.erode(mask, None, iterations=2) # type: ignore
        mask = openCv.dilate(mask, None, iterations=2) # type:ignore

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