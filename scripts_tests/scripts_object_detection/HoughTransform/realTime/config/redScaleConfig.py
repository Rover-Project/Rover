from picamera2 import Picamera2
import cv2 as openCv
import numpy
import time

def redCircleDetect(configHough: dict, nameFile):
    # Inicializa a câmera
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (configHough["h"], configHough["w"])})
    picam.configure(config)
    picam.start()

    time.sleep(1)

    print("Detectando esferas. Pressione 'q' para sair.")

    # Faixa de vermelho detectado pela camera, necessario ajustar
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
            minDist=configHough["minDist"],
            param1=100,
            param2=configHough["accumulator"],
            minRadius=configHough["minRadius"],
            maxRadius=configHough["maxRadius"]
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
        
        key = (openCv.waitKey(1) & 0xFF)

        if key == ord('q'):
            break
        
        if key == ord('s'):
            saveConfig(configHough, nameFile)

    picam.stop()
    openCv.destroyAllWindows()


if __name__ == "__main__":
    try:
        width = int(input("Digite a largura da imagem: "))
        height = int(input("Digite a altura da imagen: "))
        accumulator = int(input("Digite o valor do acumulador: "))
        minDist = float(input("Digite a distância mínima entre as esferas: "))
        minRadius = int(input("Digite o raio mínimo para as esferas: "))
        maxRadius = int(input("Digite o raio máximo para as esferas: "))
        nameFile = input("Nome do arquivo json para salvar a configuração: ")

        config = {"accumulator": accumulator, "minDist": minDist, "minRadius": minRadius, "maxRadius": maxRadius, "h": height, "w": width}
        redCircleDetect(config, nameFile)

    except:
        print("Erro na leitura da configuração da hough transform!")