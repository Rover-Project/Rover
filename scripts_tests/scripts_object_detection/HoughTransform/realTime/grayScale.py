from picamera2 import Picamera2
import cv2 as openCv
import numpy 
import time

def main(h=680, w=480, minDist=40, minRadius=10, maxRadius=120):
    # Inicializa a câmera
    picam = Picamera2()

    camera_config = picam.create_preview_configuration(main={"format": "RGB888", "size": (h, w)}) # Config 
    picam.configure(camera_config)
    picam.start()

    time.sleep(1)  # pequeno delay para estabilizar a câmera

    print("Iniciando detecção de círculos com HoughCircles. Pressione 'q' para sair.")

    while True:
        # Captura o frame da câmera
        frame = picam.capture_array()

        # Converte para escala de cinza, tentar depois somente com vermelho
        gray = openCv.cvtColor(frame, openCv.COLOR_RGB2GRAY)

        # Reduz o ruído para melhorar a detecção
        grayImage = openCv.GaussianBlur(gray, (9, 9), 2)

        # Detecção de círculos usando Hough
        circles = openCv.HoughCircles(
            grayImage,
            openCv.HOUGH_GRADIENT,
            dp=1.2,           # razão de resolução
            minDist=minDist,       # distância mínima entre centros
            param1=100,       # limite do Canny
            param2=50,        # limiar para detectar centro do círculo
            minRadius=minRadius,     # raio mínimo
            maxRadius=maxRadius     # raio máximo
        )

        # Se encontrou círculos
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))

            for (x, y, r) in circles[0, :]:
                # Desenha o círculo na imagem
                openCv.circle(frame, (x, y), r, (0, 255, 0), 2)
                
                # Desenha o centro do círculo
                openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)
                
                # Mostra coordenadas no frame
                openCv.putText(frame, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                            openCv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Mostra o frame
        openCv.imshow("Deteccao de Esferas - HoughCircles", frame)
        openCv.imshow("Imagem depois do pre-processamento", grayImage)

        # Tecla para sair
        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    openCv.destroyAllWindows()

if __name__ == "_main_":
    main()