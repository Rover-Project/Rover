import cv2 as opencv
import mediapipe 
 
# Função de classificação de gestos 
def dedos_levantados(hand_landmarks):
    pontos = hand_landmarks.landmark

    dedos = []

    # Polegar
    dedos.append(
        1 if pontos[4].x < pontos[3].x else 0
    )

    # Indicador
    dedos.append(
        1 if pontos[8].y < pontos[6].y else 0
    )

    # Médio
    dedos.append(
        1 if pontos[12].y < pontos[10].y else 0
    )

    # Anelar
    dedos.append(
        1 if pontos[16].y < pontos[14].y else 0
    )

    # Mínimo
    dedos.append(
        1 if pontos[20].y < pontos[18].y else 0
    )
    
    return dedos


if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 640

    ESP32_IP = "192.168.4.1" 
    URL_STREAM = f"http://{ESP32_IP}:81/stream"

    # Inicializa a captura de vídeo apontando para a URL da ESP32
    camera = opencv.VideoCapture(URL_STREAM)

    camera.set(opencv.CAP_PROP_BUFFERSIZE, 1)
    camera.set(opencv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    camera.set(opencv.CAP_PROP_FRAME_WIDTH, WIDTH)

    mp_drawing = mediapipe.solutions.drawing_utils
    mp_hands = mediapipe.solutions.hands

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5
    ) as hands: 
        
        while True:
            ret, frame = camera.read()
            
            frame = opencv.resize(frame, (HEIGHT, WIDTH), interpolation=opencv.INTER_CUBIC)
            
            if ret:
                height, width, _ = frame.shape
                frame = opencv.flip(frame, 1)
                frame = opencv.rotate(frame, opencv.ROTATE_180)
                frame_rgb = opencv.cvtColor(frame, opencv.COLOR_BGR2RGB)
                
                results = hands.process(frame_rgb)
                
                if results.multi_hand_landmarks is not None:
                    for hand_landmarks in results.multi_hand_landmarks:

                        dedos = dedos_levantados(hand_landmarks)

                        gesto = "Desconhecido"

                        if dedos == [0, 0, 0, 0, 0]:
                            gesto = "Punho Fechado"

                        elif dedos == [1, 1, 1, 1, 1]:
                            gesto = "Mao Aberta"

                        elif dedos == [0, 1, 1, 0, 0]:
                            gesto = "Vitoria"

                        elif dedos == [1, 0, 0, 0, 0]:
                            gesto = "Polegar"

                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )

                        opencv.putText(
                            frame,
                            gesto,
                            (20, 50),
                            opencv.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )
                        
                opencv.imshow("Frame", frame)
                if opencv.waitKey(1) & 0XFF == ord("q"):
                    break
            
        
    camera.release()
    opencv.destroyAllWindows()