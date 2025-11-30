"""
Reconhecimento de Gestos com MediaPipe.

utilizando o modelo GestureRecognizer do MediaPipe para detectar
gestos das mãos em tempo real através da câmera.

Gestos detectados:
- Thumbs Up (Polegar para cima)
- Thumbs Down (Polegar para baixo)
- Pointing Up (Apontando para cima)
- Victory (Sinal de vitória)
- Open Palm (Palma aberta)
- Closed Fist (Punho fechado)

Uso:
    python test_gesture_recognition.py [--camera-id 0]
    
Controles:
    - Pressione 'q' para sair
    - Pressione 's' para capturar screenshot
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time
import argparse


class GestureRecognitionTest:
    def __init__(self, camera_id=0):
        """
        Inicializa o teste de reconhecimento de gestos.
        
        Args:
            camera_id: ID da câmera (padrão: 0)
        """
        self.camera_id = camera_id
        self.frame_count = 0
        self.fps = 0
        self.start_time = time.time()
        
        # Carrega o modelo
        self._load_model()
        
    def _load_model(self):
        """Carrega o modelo GestureRecognizer do MediaPipe."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'gesture_recognizer.task')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo não encontrado em: {model_path}\n"
                f"Certifique-se de que 'gesture_recognizer.task' está na pasta tests/"
            )
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO
        )
        
        self.recognizer = vision.GestureRecognizer.create_from_options(options)
        print(f"✓ Modelo carregado: {model_path}")
        
    def _calculate_fps(self):
        """Calcula FPS em tempo real."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps
    
    def _draw_info(self, frame, gesture_name, confidence):
        """Desenha informações na tela."""
        height, width, _ = frame.shape
        
        # Calcula FPS
        fps = self._calculate_fps()
        
        # Desenha FPS no canto superior direito
        cv2.putText(frame, f"FPS: {fps:.1f}", (width - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Desenha gesto detectado
        if gesture_name:
            color = (0, 255, 0)  # Verde
            text = f"Gesto: {gesture_name} ({confidence:.2f})"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            
            # Background para texto
            cv2.rectangle(frame, (10, 40), (10 + text_size[0], 70 + text_size[1]), 
                         color, -1)
            cv2.putText(frame, text, (20, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        else:
            cv2.putText(frame, "Nenhum gesto detectado", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def run(self):
        """Executa o teste de reconhecimento de gestos."""
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"Erro ao abrir câmera (ID: {self.camera_id})")
        
        # Configura resolução
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f"\n Câmera aberta (ID: {self.camera_id})")
        print(" Pressione 'q' para sair | 's' para capturar screenshot\n")
        
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
                
                # Detecção de gesto
                result = self.recognizer.recognize_for_video(mp_image, timestamp)
                
                # Extrai resultado
                gesture_name = None
                confidence = 0
                if result.gestures:
                    top_gesture = result.gestures[0][0]
                    gesture_name = top_gesture.category_name
                    confidence = top_gesture.score
                
                # Desenha informações
                self._draw_info(frame, gesture_name, confidence)
                
                # Exibe frame
                cv2.imshow("Reconhecimento de Gestos", frame)
                
                # Controles
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n Saindo...")
                    break
                elif key == ord('s'):
                    filename = f"gesture_{int(time.time())}.png"
                    cv2.imwrite(filename, frame)
                    print(f" Screenshot salvo: {filename}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Teste finalizado")


def main():
    parser = argparse.ArgumentParser(
        description="Teste de reconhecimento de gestos com MediaPipe"
    )
    parser.add_argument("--camera-id", type=int, default=0,
                       help="ID da câmera (padrão: 0)")
    args = parser.parse_args()
    
    try:
        test = GestureRecognitionTest(camera_id=args.camera_id)
        test.run()
    except Exception as e:
        print(f"Erro: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
