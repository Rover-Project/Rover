import os
import cv2
import time

ESP32_IP = "192.168.1.15" 
URL_STREAM = f"http://{ESP32_IP}:81/stream"

# Inicializa a captura de vídeo apontando para a URL da ESP32
capture = cv2.VideoCapture(URL_STREAM)
# Configura buffers menores para reduzir o delay (opcional, mas ajuda na Rasp)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not capture.isOpened():
    print("Erro: Não foi possível conectar ao stream. Verifique o IP ou se a ESP32 está ligada.")
    exit()

while True:
    ret, frame = capture.read()

    if not ret:
        print("Falha ao receber frame. Tentando reconectar")
        time.sleep(1)
        continue

    cv2.imshow("Stream ESP32-CAM", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
print("Transmissão encerrada")