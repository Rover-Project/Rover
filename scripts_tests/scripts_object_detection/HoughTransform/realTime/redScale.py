from picamera2 import Picamera2
import cv2 as openCv
import numpy
import time
import sys

def main(acumulado: int, h=680, w=480, minDist=200, minRadius=10, maxRadius=120):
    # Inicializa a câmera
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (h, w)})
    picam.configure(config)
    picam.start()

    time.sleep(1)

    print("Detectando esferas na cor capturada (H≈120). Pressione 'q' para sair.")

    # representacao HSV para a cor vermelha
    lower_color = numpy.array([115, 200, 100])
    upper_color = numpy.array([130, 255, 255])

    # Kernel para limpeza da máscara
    kernel = numpy.ones((5, 5), numpy.uint8)

    while True:
        frame = picam.capture_array()

        # Converter para HSV
        hsv = openCv.cvtColor(frame, openCv.COLOR_RGB2HSV)

        # Criar máscara da cor detectada pela câmera
        mask = openCv.inRange(hsv, lower_color, upper_color)

        # Limpar máscara
        mask = openCv.morphologyEx(mask, openCv.MORPH_OPEN, kernel)
        mask = openCv.morphologyEx(mask, openCv.MORPH_CLOSE, kernel)
        mask = openCv.GaussianBlur(mask, (9, 9), 2)

        # HoughCircles na máscara
        circles = openCv.HoughCircles(
            mask,
            openCv.HOUGH_GRADIENT,
            dp=1.2,
            minDist=minDist,
            param1=100,
            param2=acumulado,
            minRadius=minRadius,
            maxRadius=maxRadius
        )

        # Desenhar círculos detectados
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))

            for (x, y, r) in circles[0, :]:
                openCv.circle(frame, (x, y), r, (0, 255, 0), 2)  # círculo
                openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)  # centro
                openCv.putText(
                    frame, 
                    f"({x},{y}) r={r}", 
                    (x - 40, y - r - 10),
                    openCv.FONT_HERSHEY_SIMPLEX, 
                    0.5, 
                    (255, 255, 255), 
                    2
                )

        # Mostrar imagens
        openCv.imshow("Deteccao da Cor Capturada", frame)
        openCv.imshow("Mascara Atual", mask)

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    openCv.destroyAllWindows()


if __name__ == "__main__":
    try:
        acumulado = int(sys.argv[1])
        main(acumulado)
    except:
        print("Erro ao pegar o acumulador!")