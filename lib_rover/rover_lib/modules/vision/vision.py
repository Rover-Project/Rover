import cv2
import numpy as np

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

    def process_frame_for_line_following(self, frame):
        """
        Processa o frame para detectar uma linha e calcular o desvio do centro.

        Args:
            frame (np.array): Frame de entrada no formato BGR.

        Retorna:
            tuple: (desvio, frame_processado)
                desvio (float): Valor entre -1.0 (totalmente à esquerda) e 1.0 (totalmente à direita).
                                0.0 significa que a linha está centralizada.
                frame_processado (np.array): Frame com as marcações de processamento (opcional, para debug).
        """
        if frame is None:
            return 0.0, None

        # 1. Converter para HSV (Hue, Saturation, Value)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. Definir o intervalo de cor da linha (Exemplo: Linha Branca)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 25, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # 3. Aplicar uma região de interesse (ROI)
        roi_start_y = int(self.height * 0.8)
        mask[:roi_start_y, :] = 0
        
        # 4. Encontrar o centroide (Momento) da linha detectada
        M = cv2.moments(mask)

        desvio = 0.0
        cx = -1 # Coordenada X do centroide

        frame_processado = frame.copy()

        if M["m00"] > 0:
            # Calcular o centroide
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cv2.circle(frame_processado, (cx, cy), 5, (0, 255, 0), -1)

            # 5. Calcular o desvio
            center_x = self.width / 2
            desvio = (cx - center_x) / center_x
        
        # Desenhar a linha central para referência
        cv2.line(frame_processado, (int(self.width/2), self.height), (int(self.width/2), roi_start_y), (255, 0, 0), 2)
        
        cv2.putText(frame_processado, f"Desvio: {desvio:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return desvio, frame_processado

    def detect_obstacle(self, frame, min_area_threshold=5000, color_range=None):
        """
        Detecta um obstáculo na frente do Rover com base na cor e tamanho.

        Args:
            frame (np.array): Frame de entrada no formato BGR.
            min_area_threshold (int): Área mínima (em pixels) para considerar um objeto como obstáculo.
            color_range (tuple, optional): Tupla (lower_hsv, upper_hsv) para a cor do obstáculo.
                                           Padrão: Vermelho (cor comum para cones ou barreiras).

        Retorna:
            tuple: (obstacle_detected, frame_processado)
                obstacle_detected (bool): True se um obstáculo for detectado.
                frame_processado (np.array): Frame com as marcações de detecção (para debug).
        """
        if frame is None:
            return False, None

        # Cor padrão: Vermelho (pode ser ajustado para o TCC)
        if color_range is None:
            # Vermelho tem dois intervalos em HSV
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
        else:
            lower_hsv, upper_hsv = color_range
            lower_red1 = lower_hsv
            upper_red1 = upper_hsv
            lower_red2 = np.array([0, 0, 0]) # Ignora o segundo intervalo se um range específico for fornecido
            upper_red2 = np.array([0, 0, 0])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Cria as máscaras para os dois intervalos de vermelho
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        # Aplica operações morfológicas para remover ruído
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Encontra contornos na máscara
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        obstacle_detected = False
        frame_processado = frame.copy()

        if len(contours) > 0:
            # Encontra o maior contorno (assumindo que o obstáculo é o maior objeto)
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > min_area_threshold:
                obstacle_detected = True
                # Desenha o contorno e o retângulo delimitador no frame de debug
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame_processado, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame_processado, "OBSTACULO", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame_processado, f"Area: {area}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.putText(frame_processado, f"Obstaculo: {obstacle_detected}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return obstacle_detected, frame_processado

# exemplo de uso (para testes)
if __name__ == "__main__":
    
    test_width, test_height = 640, 480
    test_frame = np.zeros((test_height, test_width, 3), dtype=np.uint8)
    
    
    cv2.rectangle(test_frame, (250, 200), (400, 350), (0, 0, 255), -1) # desenha um quadrado vermelho no centro
    
    vision = VisionModule((test_width, test_height))
    
    # Teste de detecção de linha (apenas para garantir que a função anterior ainda funciona)
    desvio, processed_line_frame = vision.process_frame_for_line_following(test_frame)
    print(f"Desvio de linha (com obstáculo): {desvio}")
    
    # Teste de detecção de obstáculo
    obstacle_detected, processed_obstacle_frame = vision.detect_obstacle(test_frame, min_area_threshold=1000)
    
    print(f"Obstáculo detectado: {obstacle_detected}")
    
    
    if processed_obstacle_frame is not None:    # salva o frame processado para visualização
        cv2.imwrite("test_obstacle_frame.jpg", processed_obstacle_frame)
        print("Frame de teste de obstáculo salvo como 'test_obstacle_frame.jpg'")
    else:
        print("Falha no processamento do frame de teste de obstáculo.")
