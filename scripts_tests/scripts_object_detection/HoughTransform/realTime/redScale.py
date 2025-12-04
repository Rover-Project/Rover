from picamera2 import Picamera2
import cv2 as openCv
import numpy
import time
import sys

def main(acumulado: int, h=680, w=480, minDist=200, minRadius=10, maxRadius=120):
    # Inicializa a câmera
    picam = Picamera2()

    camera_config = picam.create_preview_configuration(main={"format": "RGB888", "size": (h, w)})
    picam.configure(camera_config)
    picam.start()

    time.sleep(1)

    print("Iniciando detecção de esferas VERMELHAS com HoughCircles. Pressione 'q' para sair.")

    while True:
        frame = picam.capture_array()

        # Converter para HSV 
        hsv = openCv.cvtColor(frame, openCv.COLOR_RGB2HSV)

        # Faixa de vermelho
        lower_red1 = numpy.array([0, 100, 80])
        upper_red1 = numpy.array([10, 255, 255])

        lower_red2 = numpy.array([170, 100, 80])
        upper_red2 = numpy.array([180, 255, 255])

        # Criar máscaras
        mask1 = openCv.inRange(hsv, lower_red1, upper_red1)
        mask2 = openCv.inRange(hsv, lower_red2, upper_red2)

        redImage = openCv.bitwise_or(mask1, mask2)

        redImage = openCv.GaussianBlur(redImage, (9, 9), 2)

        # HoughCircles na máscara
        circles = openCv.HoughCircles(
            redImage,
            openCv.HOUGH_GRADIENT,
            dp=1.2,
            minDist=minDist,
            param1=100,
            param2=acumulado, # Bom parametro para o acumulador de redScale     
            minRadius=minRadius,
            maxRadius=maxRadius
        )

        # Desenhar círculos detectados
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))

            for (x, y, r) in circles[0, :]:
                openCv.circle(frame, (x, y), r, (0, 255, 0), 2)  # círculo
                openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)  # centro
                openCv.putText(frame, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                            openCv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        openCv.imshow("Deteccao de Esferas Vermelhas", frame)

        openCv.imshow("Mascara Vermelha", redImage)

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    openCv.destroyAllWindows()


if __name__ == "__main__":
    
    try:
        acumulado = int(sys.argv[1])
        main(acumulado)
    except:
        print("Erro ao pegar o acumulador")
    
