import cv2 as openCV
import sys 
from pathlib import Path
import numpy

try:
    file = sys.argv[1]
except IndexError:
    print("vode nao passou o arquivo que deseja abrir")
    file = None
    
path = Path(__file__).parent / "assets" / file # type: ignore

# Tecnica de binarizacao adptativa 
def binaryOtsu(img):
    
    otsu = openCV.THRESH_BINARY + openCV.THRESH_OTSU
    
    return openCV.threshold(
        img,
        0,
        255,
        otsu
    )

def lineDetectHough(img, isCut=False):

    height, width = img.shape[:2]
    
    if isCut:
        cut = img[int(height * 0.6):height, 0:width]
    else:
        cut = img 
        
    gray = openCV.cvtColor(cut, openCV.COLOR_BGR2GRAY)
    
    # Filtro de passas baixas para reduzis bordas internas 
    blur = openCV.GaussianBlur(gray, (5, 5), 0)

    # Encontra bordas
    edges = openCV.Canny(blur, 50, 150)
    
    # Realiza operacao morfologia para "engrossar" possiveis linhas
    structElement = openCV.getStructuringElement(
        openCV.MORPH_RECT, 
        (3, 3)
    )
    
    edges = openCV.dilate(
        edges, 
        structElement, 
        iterations=1
    )

    # Detect linhas 
    lines = openCV.HoughLinesP(
        edges,
        rho=1,
        theta=numpy.pi / 180,
        threshold=40,
        minLineLength=60,
        maxLineGap=20
    )

    # Desenha linhas 
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            openCV.line(cut, (x1, y1), (x2, y2), (0, 255, 0), 2)

if __name__ == "__main__":
    if file is not None:
        
        img = openCV.imread(path)
        
        if img is not None:
            
            img = openCV.resize(
                img, 
                (640, 640),
                interpolation=openCV.INTER_CUBIC
            )
        
            lines = img.copy()
            
            lineDetectHough(lines)
          
            openCV.imshow("Imagem", img)
            openCV.imshow("Linhas", lines)
        
            key = openCV.waitKey() & 0xFF
            
            if key == ord('q'):
                openCV.destroyAllWindows()