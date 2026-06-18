import os
import cv2
import time

ESP32_IP = "192.168.4.1" 
URL_STREAM = f"http://{ESP32_IP}:81/stream"

# Inicializa a captura de vídeo apontando para a URL da ESP32
capture = cv2.VideoCapture(URL_STREAM)

capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

NOME_JANELA = "Stream ESP32-CAM"
cv2.namedWindow(NOME_JANELA, cv2.WINDOW_NORMAL)

cv2.resizeWindow(NOME_JANELA, 800, 600)

if not capture.isOpened():
    print("Erro: Não foi possível conectar ao stream. Verifique o IP ou se a ESP32 está ligada.")
    exit()

while True:
    ret, frame = capture.read()

    if not ret:
        print("Falha ao receber frame. Tentando reconectar")
        continue

    cv2.imshow(NOME_JANELA, frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
print("Transmissão encerrada")