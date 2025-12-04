from picamera2 import Picamera2
import cv2 as openCv
import numpy
import time
import sys

from picamera2 import Picamera2
import cv2 as openCv
import numpy
import time
import sys

def redCircleDetect(acumulado: int, h=680, w=480, minDist=200, minRadius=10, maxRadius=120):
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (h, w)})
    picam.configure(config)
    picam.start()

    time.sleep(1)

    print("Iniciando detecção de esferas VERMELHAS. Pressione 'q' para sair.")

    while True:
        frame = picam.capture_array()

        hsv = openCv.cvtColor(frame, openCv.COLOR_RGB2HSV)

        # Faixa ajustada de vermelho
        lower_red1 = numpy.array([0, 70, 50])
        upper_red1 = numpy.array([10, 255, 255])
        lower_red2 = numpy.array([170, 70, 50])
        upper_red2 = numpy.array([180, 255, 255])

        mask1 = openCv.inRange(hsv, lower_red1, upper_red1)
        mask2 = openCv.inRange(hsv, lower_red2, upper_red2)
        redImage = openCv.bitwise_or(mask1, mask2)

        # Limpeza da máscara
        kernel = numpy.ones((5, 5), numpy.uint8)
        redImage = openCv.morphologyEx(redImage, openCv.MORPH_OPEN, kernel)
        redImage = openCv.morphologyEx(redImage, openCv.MORPH_CLOSE, kernel)
        redImage = openCv.GaussianBlur(redImage, (9, 9), 2)

        # Hough Circle
        circles = openCv.HoughCircles(
            redImage,
            openCv.HOUGH_GRADIENT,
            dp=1.2,
            minDist=minDist,
            param1=100,
            param2=acumulado,
            minRadius=minRadius,
            maxRadius=maxRadius
        )

        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))
            for (x, y, r) in circles[0, :]:
                openCv.circle(frame, (x, y), r, (0, 255, 0), 2)
                openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)
                openCv.putText(frame, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                               openCv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        openCv.imshow("Deteccao de Vermelho", frame)
        openCv.imshow("Mascara Vermelha", redImage)

        if openCv.waitKey(1) & 0xFF == 'q':
            break

    picam.stop()
    openCv.destroyAllWindows()



if __name__ == "__main__":
    
    try:
        acumulado = int(sys.argv[1])
        redCircleDetect(acumulado)
    except:
        print("Erro ao pegar o acumulador!")
    
