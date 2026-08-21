import cv2
import time
import subprocess
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

# Utilitários de desenho
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

latest_result = None

def save_result(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_result
    latest_result = result

def main():
    width, height = 640, 480
    
    # O codec nativo para vídeo bruto no rpicam-vid é yuv420
    cmd = [
        'rpicam-vid', '-t', '0',
        '--codec', 'yuv420',
        '--width', str(width),
        '--height', str(height),
        '--framerate', '30',
        '--nopreview',
        '-o', '-'
    ]
    
    # Deixando o stderr livre para vermos se a câmera reclama de algo no terminal
    camera_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=save_result,
        num_hands=1 
    )

    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        print("Bypass de câmera iniciado. Lendo fluxo YUV420. Pressione 'q' para sair.")
        
        # O tamanho de um frame YUV420 na memória é Largura x Altura x 1.5
        frame_bytes_size = int(width * height * 1.5)
        
        while True:
            # Lê exatamente 1 frame do fluxo de dados
            raw_frame = camera_process.stdout.read(frame_bytes_size)
            
            if len(raw_frame) != frame_bytes_size:
                print(f"Fim do fluxo! Bytes recebidos: {len(raw_frame)}. Verifique se há erros da câmera acima.")
                break

            # Converte YUV420 puro para uma matriz e depois para RGB (3 canais)
            yuv_frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((int(height * 1.5), width))
            frame_rgb = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2RGB_I420)
            
            # Envia para o MediaPipe
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            frame_timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, frame_timestamp_ms)

            # Para desenhar a janela do OpenCV, precisamos de BGR
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if latest_result:
                if latest_result.gestures:
                    top_gesture = latest_result.gestures[0][0]
                    texto_gesto = f"Gesto: {top_gesture.category_name} ({top_gesture.score:.2f})"
                    cv2.putText(frame_bgr, texto_gesto, (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                if latest_result.hand_landmarks:
                    for hand_landmarks in latest_result.hand_landmarks:
                        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                        hand_landmarks_proto.landmark.extend([
                            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z) 
                            for lm in hand_landmarks
                        ])
                        mp_drawing.draw_landmarks(
                            frame_bgr,
                            hand_landmarks_proto,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())

            cv2.imshow('Rover - Reconhecimento de Gestos (Nativo Pi 5)', frame_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    camera_process.terminate()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
