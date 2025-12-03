from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Configurações para detecção de círculos (ajustadas para olhos)
MIN_DIST = 40
MIN_RADIUS = 15
MAX_RADIUS = 50

def detectar_olhos_picam(h=640, w=480):
    
    # 1. Configurar e Iniciar a Câmera
    picam = Picamera2()
    
    # Configuração da câmera: define o formato e o tamanho da imagem de saída
    camera_config = picam.create_preview_configuration(
        main={"format": "RGB888", "size": (h, w)}
    )
    picam.configure(camera_config)
    picam.start()

    time.sleep(1) # Pequeno delay para estabilizar o sensor

    print("Iniciando detecção de olhos via Picamera2. Pressione 'q' para sair.")

    try:
        while True:
            # 2. Captura do Frame
            # picam.capture_array() retorna um array NumPy (RGB)
            frame = picam.capture_array()
            output = frame.copy()
            
            # Converte de RGB para BGR (formato esperado pelo OpenCV)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 3. Processamento
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)

            # 4. Detecção de círculos (olhos) usando HoughCircles
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=MIN_DIST,
                param1=100,
                param2=30,  # Limiar de votos do centro do círculo
                minRadius=MIN_RADIUS,
                maxRadius=MAX_RADIUS
            )

            # 5. Desenhar Círculos
            if circles is not None:
                circles = np.uint16(np.around(circles))

                for (x, y, r) in circles[0, :]:
                    # Desenha o círculo na imagem original (output BGR)
                    cv2.circle(frame_bgr, (x, y), r, (0, 255, 0), 2)  # Contorno
                    cv2.circle(frame_bgr, (x, y), 2, (0, 0, 255), 3)  # Centro
                    
                    # Opcional: Exibe o raio e o centro
                    cv2.putText(frame_bgr, f"r={r}", (x + 10, y - r), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 6. Mostrar o resultado
            cv2.imshow('Deteccao de Olhos - Ao Vivo (PiCam)', frame_bgr)

            # 7. Interromper o loop: Pressione 'q' para sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Garante que a câmera e as janelas sejam fechadas
        picam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detectar_olhos_picam()
