"""
Detecção de Objetos com MediaPipe. (Abordagem para detectar bola vermelha)

utilizando segmentação de cor HSV combinada com detecção de forma
para identificar objetos específicos em tempo real através
da câmera.

Abordagem híbrida:
- Segmentação HSV para detectar pixels da cor desejada
- Morfologia para limpar ruído
- Detecção de círculos (HoughCircles) para validar forma
- Contornos para encontrar a região de interesse

Uso:
    python test_object_detection.py [--camera-id 0] [--color red]
    
Controles:
    - Pressione 'q' para sair
    - Pressione 's' para capturar screenshot
    - Pressione 'c' para calibrar cores
"""

import cv2
import numpy as np
import time
import argparse
from typing import Tuple, Optional


class ObjectDetectionTest:
    """Detector de objetos baseado em segmentação de cor e forma."""
    
    # Definições de cores em HSV
    COLOR_RANGES = {
        'red': [
            ((0, 100, 100), (10, 255, 255)),
            ((160, 100, 100), (180, 255, 255))
        ],
        'blue': [
            ((100, 100, 100), (130, 255, 255)),
        ],
        'green': [
            ((40, 100, 100), (80, 255, 255)),
        ],
        'yellow': [
            ((20, 100, 100), (40, 255, 255)),
        ]
    }
    
    def __init__(self, camera_id=0, color='red', min_radius=10, max_radius=200):
        """        
        Args:
            camera_id: ID da câmera (padrão: 0)
            color: Cor do objeto a detectar (padrão: 'red')
            min_radius: Raio mínimo do círculo em pixels
            max_radius: Raio máximo do círculo em pixels
        """
        self.camera_id = camera_id
        self.color = color.lower()
        self.min_radius = min_radius
        self.max_radius = max_radius
        
        if self.color not in self.COLOR_RANGES:
            raise ValueError(f"Cor não suportada: {color}. "
                           f"Opções: {', '.join(self.COLOR_RANGES.keys())}")
        
        self.frame_count = 0
        self.fps = 0
        self.start_time = time.time()
        
        print(f" Configurado para detectar objetos {self.color.upper()}")
        print(f" Raio do círculo: {min_radius} - {max_radius} pixels\n")
    
    def _calculate_fps(self):
        """Calcula FPS em tempo real."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps
    
    def _create_mask(self, frame_hsv):
        """
        Cria máscara para a cor especificada.
        
        Args:
            frame_hsv: Frame em formato HSV
            
        Returns:
            Máscara binária
        """
        mask = None
        for lower, upper in self.COLOR_RANGES[self.color]:
            submask = cv2.inRange(frame_hsv, lower, upper)
            if mask is None:
                mask = submask
            else:
                mask = cv2.bitwise_or(mask, submask)
        
        # Morfologia para limpar ruído
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _find_contours(self, mask):
        """
        Encontra contornos na máscara.
        
        Args:
            mask: Máscara binária
            
        Returns:
            Lista de contornos
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def _detect_circles(self, mask, frame):
        """
        Detecta círculos usando HoughCircles.
        
        Args:
            mask: Máscara binária
            frame: Frame original
            
        Returns:
            Coordenadas dos círculos (x, y, raio) ou None
        """
        circles = cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )
        
        return circles
    
    def _draw_detections(self, frame, circles, contours):
        """
        Desenha detecções na frame.
        
        Args:
            frame: Frame original
            circles: Círculos detectados
            contours: Contornos detectados
        """
        height, width, _ = frame.shape
        
        # Desenha contornos
        if contours:
            cv2.drawContours(frame, contours, -1, (0, 255, 255), 2)
        
        # Desenha círculos
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                radius = i[2]
                
                # Desenha círculo e centro
                cv2.circle(frame, center, radius, (0, 255, 0), 3)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                
                # Informações
                text = f"r={radius}px"
                cv2.putText(frame, text, (center[0] - 30, center[1] - radius - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                return True, center, radius
        
        return False, None, None
    
    def _draw_info(self, frame, detected, center=None, radius=None):
        """Desenha informações gerais na tela."""
        height, width, _ = frame.shape
        
        # FPS
        fps = self._calculate_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (width - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Status de detecção
        if detected:
            status = f"Objeto {self.color.upper()} detectado!"
            color = (0, 255, 0)
        else:
            status = f"Procurando por objeto {self.color.upper()}..."
            color = (0, 0, 255)
        
        cv2.putText(frame, status, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Instruções
        cv2.putText(frame, "q: sair | s: screenshot | c: calibrar", 
                   (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _show_hsv_calibration(self, frame, frame_hsv):
        """
        Exibe informações HSV do pixel central para calibração.
        
        Args:
            frame: Frame original
            frame_hsv: Frame em HSV
        """
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        
        # Obtém valor HSV no centro
        h, s, v = frame_hsv[center_y, center_x]
        
        # Desenha indicador no centro
        cv2.circle(frame, (center_x, center_y), 5, (255, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 20, (255, 255, 0), 1)
        
        # Mostra valores
        text = f"HSV: ({h}, {s}, {v})"
        cv2.putText(frame, text, (center_x - 80, center_y - 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    def run(self, calibration_mode=False):
        """
        Executa o teste de detecção de objetos.
        
        Args:
            calibration_mode: Se True, mostra valores HSV para calibração
        """
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"Erro ao abrir câmera (ID: {self.camera_id})")
        
        # Configura resolução
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f" Câmera aberta (ID: {self.camera_id})")
        print(" Pressione 'q' para sair | 's' para screenshot | 'c' para calibrar\n")
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Erro ao ler frame")
                    break
                
                # Espelha a imagem
                frame = cv2.flip(frame, 1)
                
                # Converte para HSV
                frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Cria máscara
                mask = self._create_mask(frame_hsv)
                
                # Detecta formas
                contours = self._find_contours(mask)
                circles = self._detect_circles(mask, frame)
                
                # Desenha detecções
                detected, center, radius = self._draw_detections(frame, circles, contours)
                
                # Desenha informações
                self._draw_info(frame, detected, center, radius)
                
                # Modo calibração
                if calibration_mode:
                    self._show_hsv_calibration(frame, frame_hsv)
                
                # Exibe frame
                cv2.imshow("Detecção de Objetos", frame)
                
                # Exibe máscara em segunda janela
                cv2.imshow("Máscara HSV", mask)
                
                # Controles
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n Saindo...")
                    break
                elif key == ord('s'):
                    filename = f"detection_{int(time.time())}.png"
                    cv2.imwrite(filename, frame)
                    print(f" Screenshot salvo: {filename}")
                elif key == ord('c'):
                    calibration_mode = not calibration_mode
                    mode_text = "ATIVADO" if calibration_mode else "DESATIVADO"
                    print(f" Modo calibração {mode_text}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(" Teste finalizado")


def main():
    parser = argparse.ArgumentParser(
        description="Teste de detecção de objetos com MediaPipe e HSV"
    )
    parser.add_argument("--camera-id", type=int, default=0,
                       help="ID da câmera (padrão: 0)")
    parser.add_argument("--color", type=str, default="red",
                       choices=["red", "blue", "green", "yellow"],
                       help="Cor do objeto a detectar (padrão: red)")
    parser.add_argument("--min-radius", type=int, default=10,
                       help="Raio mínimo do círculo em pixels (padrão: 10)")
    parser.add_argument("--max-radius", type=int, default=200,
                       help="Raio máximo do círculo em pixels (padrão: 200)")
    args = parser.parse_args()
    
    try:
        test = ObjectDetectionTest(
            camera_id=args.camera_id,
            color=args.color,
            min_radius=args.min_radius,
            max_radius=args.max_radius
        )
        test.run()
    except Exception as e:
        print(f"Erro: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
