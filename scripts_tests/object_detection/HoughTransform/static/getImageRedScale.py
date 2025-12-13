import cv2 as openCv
import numpy
import sys
from pathlib import Path

def RedCircleDetect(image_path, minDist=200, minRadius=10, maxRadius=120):

    # Carrega a imagem
    image = openCv.imread(image_path)

    if image is None:
        print("Erro: imagem não encontrada!")
        return

    print("Processando imagem para detectar esferas VERMELHAS...")

    # Converte inicialmente para HSV, metrica de definição de uma cor qualquer
    hsv = openCv.cvtColor(image, openCv.COLOR_BGR2HSV)

    # Faixas do vermelho no HSV: Hue, Saturation e value 
    lower_red1 = numpy.array([0, 100, 80]) 
    upper_red1 = numpy.array([10, 255, 255])

    lower_red2 = numpy.array([170, 100, 80])
    upper_red2 = numpy.array([180, 255, 255])

    # Criando macaras usando as faixas de vemelho definidas 
    mask1 = openCv.inRange(hsv, lower_red1, upper_red1)
    mask2 = openCv.inRange(hsv, lower_red2, upper_red2)

    redImage = openCv.bitwise_or(mask1, mask2) # Merge das duas mascaras criadas

    # Filtro para suavizar ruído
    redImage = openCv.GaussianBlur(redImage, (9, 9), 2)

    # HoughCircles na imagem
    circles = openCv.HoughCircles(
        redImage,
        openCv.HOUGH_GRADIENT,
        dp=1.2,
        minDist=minDist, # Se a distancia minima for baixa, vai identificar o reflexo e sobras tambem
        param1=100, 
        param2=30, # Bom parametro para redScale
        minRadius=minRadius,
        maxRadius=maxRadius
    )

    # Se encontrou círculos, desenhar na imagem original
    if circles is not None:
        circles = numpy.uint16(numpy.around(circles))

        for (x, y, r) in circles[0, :]:
            openCv.circle(image, (x, y), r, (0, 255, 0), 2)      # círculo
            openCv.circle(image, (x, y), 2, (0, 0, 255), 3)      # centro
            openCv.putText(
                image,
                f"({x},{y}) r={r}",
                (x - 40, y - r - 10),
                openCv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
    else:
        print("Nenhum círculo vermelho encontrado.")

    openCv.imshow("Deteccao de Esferas Vermelhas", image)
    openCv.imshow("Mascara Vermelha", redImage)

    openCv.waitKey(0)
    openCv.destroyAllWindows()


if __name__ == "__main__":
    
    # Tenta pegar o caminho da imagem via argumento de linha de comando
    try:
        path = Path(__file__).parent.parent.parent / "assets" / sys.argv[1]
    except IndexError:
        print("Nenhum caminho foi passado")
    
    try:
        RedCircleDetect(path)
    except:
        print("Error ao carregar imagem!")

    
