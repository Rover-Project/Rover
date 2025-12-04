import cv2 as openCv
import numpy
import sys 
from pathlib import Path

def main(image_path, minDist=40, minRadius=10, maxRadius=120):
    # Carrega a imagem do disco
    frame = openCv.imread(image_path)

    if frame is None:
        print("Erro: imagem não encontrada!")
        return

    print("Processando imagem para detecção de círculos...")

    # Converte para escala de cinza
    gray = openCv.cvtColor(frame, openCv.COLOR_BGR2GRAY)

    # Reduz ruído
    grayImage = openCv.GaussianBlur(gray, (9, 9), 2)
    
    # Detecção de círculos usando Hough
    circles = openCv.HoughCircles(
        grayImage,
        openCv.HOUGH_GRADIENT,
        dp=1.2,
        minDist=minDist,
        param1=100,
        param2=30,
        minRadius=minRadius,
        maxRadius=maxRadius
    )

    # Se encontrou círculos
    if circles is not None:
        circles = numpy.uint16(numpy.around(circles))

        for (x, y, r) in circles[0, :]:
            # Círculo
            openCv.circle(frame, (x, y), r, (0, 255, 0), 2)
            # Centro
            openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)
            # Texto informativo
            openCv.putText(frame, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                        openCv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    else:
        print("Nenhum círculo encontrado.")

    # Exibe a imagem final
    openCv.imshow("Deteccao de Esferas - HoughCircles", frame)
    openCv.imshow("Imagem depois do pre-processamento", grayImage)
    openCv.waitKey(0)
    openCv.destroyAllWindows()

if __name__ == "__main__":
    
    
    # Tenta pegar o caminho da imagem via argumento de linha de comando
    try:
        path = Path.home() / sys.argv[1]
    except IndexError:
        print("Nenhum caminho foi passado")
    
    try:
        main(path)
    except:
        print("Error ao carregar imagem!")
