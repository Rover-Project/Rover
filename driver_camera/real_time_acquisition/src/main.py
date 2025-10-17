from picamera2 import Picamera2 
import cv2

# Cria uma instância para controle da camera
picam2 = Picamera2()

# Cria uma configuração padrão para a visualização, ajustando a resolução.
config = picam2.create_preview_configuration(main={"size": (1280, 720)})

# Aplica a configuração criada ao objeto da câmera.
picam2.configure(config)

# Inicia a captura de vídeo.
picam2.start()


# Loop para visualização das imagens capturadas pela camera
while True:
    # Captura um frame 
    frame = picam2.capture_array()

    # Processamento
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Cria uma janela e exibe o frame processado.
    cv2.imshow("Camera em Loop", frame_bgr)

    # Controle de Saída e Latência 
    # Se a tecla pressionada for 'q' (ord('q')), o loop é interrompido.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fecha todas as janelas criadas pelo OpenCV.
cv2.destroyAllWindows()

# Interrompe a câmera Picamera2, liberando o hardware.
picam2.stop()