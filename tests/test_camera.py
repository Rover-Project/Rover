import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time


current_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(current_dir, 'gesture_recognizer.task')
# model_path = os.path.join(current_dir, 'hand_landmarker.task')


base_options = python.BaseOptions(model_asset_path=model_path)
# O modo VIDEO é crucial para a estratégia "Detectar + Rastrear" funcionar
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)

# 2. Inicialização da Câmera
# Tente index 0 ou 1 se não abrir
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Iniciando reconhecimento de gestos. Pressione 'q' para sair.")

# Usamos o bloco 'with' para garantir que o modelo seja fechado corretamente
with vision.GestureRecognizer.create_from_options(options) as recognizer:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 3. Prepara a imagem para o MediaPipe
        # O MediaPipe precisa de RGB e formato mp.Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # É necessário timestamp em milissegundos para o modo VIDEO
        timestamp = int(time.time() * 1000)

        # 4. Inferência
        recognition_result = recognizer.recognize_for_video(mp_image, timestamp)

        # 5. Lógica de Controle (Exemplo para o Rover)
        if recognition_result.gestures:
            # Pega o primeiro gesto da primeira mão detectada
            top_gesture = recognition_result.gestures[0][0]
            nome_gesto = top_gesture.category_name
            score = top_gesture.score

            if score > 0.5:
                cv2.putText(frame, f"Gesto: {nome_gesto}", (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # AQUI ENTRA SUA LÓGICA DO ROVER
                if nome_gesto == "Thumb_Up":
                    print("COMANDO: Acelerar Rover")
                elif nome_gesto == "Closed_Fist":
                    print("COMANDO: Parar Rover")
                elif nome_gesto == "Victory":
                    print("COMANDO: Girar Câmera")
        
        # Mostra na tela (opcional se for headless)
        cv2.imshow('Visao Rover', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()