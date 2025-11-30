"""
Mapeamento de Pontos de Mão (Hand Landmarks) com MediaPipe.

utilizando o modelo HandLandmarker do MediaPipe para detectar os 21 pontos
de referência (landmarks) das mãos em tempo real através da câmera.

Landmarks detectados (21 pontos por mão):
- Pulso (wrist)
- Palma (palm root e palm center)
- Dedos (thumb, index, middle, ring, pinky)

Uso:
    python test_hand_landmarks.py [--camera-id 0] [--num-hands 2]
    
Controles:
    - Pressione 'q' para sair
    - Pressione 's' para capturar screenshot
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import os
import time
import argparse
import numpy as np


class HandLandmarksTest:
    def __init__(self, camera_id=0, num_hands=2):
        """
        Inicializa o teste de mapeamento de pontos de mão.
        
        Args:
            camera_id: ID da câmera (padrão: 0)
            num_hands: Número máximo de mãos a detectar (padrão: 2)
        """
        self.camera_id = camera_id
        self.num_hands = num_hands
        self.frame_count = 0
        self.fps = 0
        self.start_time = time.time()
        
        # Configuração de drawing
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Carrega o modelo
        self._load_model()
        
    def _load_model(self):
        """Carrega o modelo HandLandmarker do MediaPipe."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'hand_landmarker.task')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo não encontrado em: {model_path}\n"
                f"Certifique-se de que 'hand_landmarker.task' está na pasta tests/"
            )
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.num_hands,
            running_mode=vision.RunningMode.VIDEO
        )
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        print(f"✓ Modelo carregado: {model_path}")
        print(f"✓ Detectando até {self.num_hands} mão(s)\n")
        
    def _calculate_fps(self):
        """Calcula FPS em tempo real."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps
    
    def _draw_landmarks(self, frame, hand_landmarks, handedness):
        """
        Desenha landmarks das mãos na imagem.
        
        Args:
            frame: Frame do vídeo
            hand_landmarks: Lista de landmarks (21 pontos)
            handedness: Informação se é mão esquerda ou direita
        """
        height, width, _ = frame.shape
        
        # Desenha conexões entre pontos
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        for landmark in hand_landmarks:
            hand_landmarks_proto.landmark.add(
                x=landmark.x, y=landmark.y, z=landmark.z
            )
        
        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks_proto,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )
    
    def _draw_info(self, frame, num_hands):
        """Desenha informações gerais na tela."""
        height, width, _ = frame.shape
        
        # FPS
        fps = self._calculate_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (width - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Número de mãos detectadas
        color = (0, 255, 0) if num_hands > 0 else (0, 0, 255)
        cv2.putText(frame, f"Maos detectadas: {num_hands}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Instruções
        cv2.putText(frame, "Pressione 'q' para sair | 's' para screenshot", 
                   (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _draw_hand_labels(self, frame, results):
        """Desenha labels de "Left" ou "Right" para cada mão."""
        height, width, _ = frame.shape
        
        for idx, handedness in enumerate(results.handedness):
            # Pega o primeiro landmark para posicionar o label
            if idx < len(results.hand_landmarks):
                wrist = results.hand_landmarks[idx][0]
                x = int(wrist.x * width)
                y = int(wrist.y * height)
                
                label = handedness[0].category_name
                confidence = handedness[0].score
                
                text = f"{label} ({confidence:.2f})"
                color = (255, 0, 0) if label == "Left" else (0, 165, 255)
                
                cv2.putText(frame, text, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def run(self):
        """Executa o teste de mapeamento de pontos de mão."""
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"Erro ao abrir câmera (ID: {self.camera_id})")
        
        # Configura resolução
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f"✓ Câmera aberta (ID: {self.camera_id})")
        print("➤ Pressione 'q' para sair | 's' para capturar screenshot\n")
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Erro ao ler frame")
                    break
                
                # Espelha a imagem
                frame = cv2.flip(frame, 1)
                
                # Converte para RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                
                # Timestamp em milissegundos
                timestamp = int(time.time() * 1000)
                
                # Detecção de landmarks
                results = self.landmarker.detect_for_video(mp_image, timestamp)
                
                # Desenha landmarks
                if results.hand_landmarks:
                    for hand_landmarks in results.hand_landmarks:
                        self._draw_landmarks(frame, hand_landmarks, None)
                    
                    self._draw_hand_labels(frame, results)
                
                # Desenha informações
                self._draw_info(frame, len(results.hand_landmarks))
                
                # Exibe frame
                cv2.imshow("Mapeamento de Pontos de Mão", frame)
                
                # Controles
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n➤ Saindo...")
                    break
                elif key == ord('s'):
                    filename = f"landmarks_{int(time.time())}.png"
                    cv2.imwrite(filename, frame)
                    print(f"✓ Screenshot salvo: {filename}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✓ Teste finalizado")


def main():
    parser = argparse.ArgumentParser(
        description="Teste de mapeamento de pontos de mão com MediaPipe"
    )
    parser.add_argument("--camera-id", type=int, default=0,
                       help="ID da câmera (padrão: 0)")
    parser.add_argument("--num-hands", type=int, default=2,
                       help="Número máximo de mãos a detectar (padrão: 2)")
    args = parser.parse_args()
    
    try:
        test = HandLandmarksTest(camera_id=args.camera_id, num_hands=args.num_hands)
        test.run()
    except Exception as e:
        print(f"Erro: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
