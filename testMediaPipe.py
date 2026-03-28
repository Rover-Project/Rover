import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

# Utilitários de desenho do MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Variável global para armazenar temporariamente o último resultado da detecção
latest_result = None

def save_result(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    """
    Função de callback chamada de forma assíncrona pelo MediaPipe sempre que 
    termina de processar um frame.
    """
    global latest_result
    latest_result = result

def main():
    # Inicializa a captura de vídeo da câmera (0 é geralmente a câmera padrão)
    # Se você tiver múltiplas câmeras, pode precisar alterar para 1, 2, etc.
    cap = cv2.VideoCapture(0)
    
    # Reduzir a resolução para aumentar o FPS na Raspberry Pi 5 (Opcional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Configurações base apontando para o arquivo do modelo baixado
    base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
    
    # Configurações do reconhecedor de gestos para tempo real
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=save_result,
        num_hands=1 # Aumente se quiser detectar mais de uma mão simultaneamente
    )

    # Cria a instância do Gesture Recognizer
    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        print("Iniciando a câmera. Pressione 'q' para sair.")
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Falha ao capturar a câmera. Ignorando frame...")
                continue

            # O OpenCV captura em BGR, mas o MediaPipe espera imagens em RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Converte para o objeto Image nativo do MediaPipe
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Gera um timestamp em milissegundos para o frame atual
            frame_timestamp_ms = int(time.time() * 1000)

            # Envia a imagem para reconhecimento assíncrono.
            # O resultado não retorna aqui, ele será jogado na função `save_result`.
            recognizer.recognize_async(mp_image, frame_timestamp_ms)

            # Se já tivemos algum resultado processado pelo callback, desenhamos no frame
            if latest_result:
                # 1. Escrever o nome do Gesto e a confiança
                if latest_result.gestures:
                    top_gesture = latest_result.gestures[0][0]
                    texto_gesto = f"Gesto: {top_gesture.category_name} ({top_gesture.score:.2f})"
                    
                    cv2.putText(frame, texto_gesto, (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                # 2. Desenhar os pontos (landmarks) da mão
                if latest_result.hand_landmarks:
                    for hand_landmarks in latest_result.hand_landmarks:
                        # Converte do formato novo da Tasks API para o formato esperado pelos drawing_utils antigos
                        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                        hand_landmarks_proto.landmark.extend([
                            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z) 
                            for lm in hand_landmarks
                        ])
                        
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks_proto,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())

            # Mostra o frame em uma janela do OpenCV
            cv2.imshow('Raspberry Pi 5 - Reconhecimento de Gestos', frame)

            # Aguarda a tecla 'q' ser pressionada para quebrar o loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Libera os recursos do hardware
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    
    
# curl -LsSf https://astral.sh/uv/install.sh | sh

# wget -O gesture_recognizer.task -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task