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

# Funcao que limita a area utilizada para desenho das linhas
def aplicar_roi(img):
    height, width = img.shape[:2]

    # Valor para retirar o capo dos carros 
    capo_offset = int(height * 0.9)

    # Definição do ROI(Region of Interest) (Ajustavel de acordo com a camera e ambiente)
    # Topo = Quanto maior o valor, mais baixo o Poligono
    bottom_left  = [width * 0, capo_offset]      # Canto inferior esquerdo 
    top_left     = [width * 0.2, height * 0.6] # Topo esquerdo 
    top_right    = [width * 0.65, height * 0.6] # Topo direito
    bottom_right = [width * 0.9, capo_offset]      # Canto inferior direito

    poligono = numpy.array([[bottom_left, top_left, top_right, bottom_right]], dtype=numpy.int32)

    # máscara preta
    mask = numpy.zeros_like(img)
    
    # Preenche o trapézio com branco
    openCV.fillPoly(mask, poligono, 255)

    # Aplica a máscara na imagem (mantém apenas o que está dentro do trapézio)
    mask_img = openCV.bitwise_and(img, mask)
    
    return mask_img

def contourDetect(img, isCut=False):
    height, width = img.shape[:2]

    if isCut:
        y_offset = int(height*0.6)
        workImage = img[y_offset, 0:width]
    else:
        y_offset = 0
        workImage = img

    # PRE-PROCESSAmENTO:
    gray = openCV.cvtColor(workImage, openCV.COLOR_BGR2GRAY)
    blur = openCV.GaussianBlur(gray, (5, 5), 0)
    cannyImg = openCV.Canny(blur, 50, 150)
    roiImg = aplicar_roi(cannyImg)
    contours, _ = openCV.findContours(roiImg, openCV.RETR_EXTERNAL, openCV.CHAIN_APPROX_NONE)

    radius = 7  
    whichContours = -1

    if contours:
        for cnt in contours:
            area = openCV.contourArea(cnt)

            if area > 50:
                momentum = openCV.moments(cnt)

                if momentum["m00"] != 0:
                    cx = int(momentum["m10"] / momentum["m00"])
                    cy = int(momentum["m01"] / momentum["m00"])

                    center = (cx, cy)

                    openCV.circle(workImage, center, radius, (255, 0, 0), 2)
                    openCV.drawContours(workImage, [cnt], whichContours, (0, 255, 0), 1)
            

    return roiImg, contours, workImage

if __name__ == "__main__":
    #img = openCV.imread(str(path))
    # img_reduce = openCV.resize(img, (640, 640), interpolation=openCV.INTER_CUBIC)
    # contourImg, contours, final = contourDetect(img_reduce) 

    video = openCV.VideoCapture(str(path))

    while True:
        ret, frame = video.read()

        if not ret:
            video = openCV.VideoCapture(path)
            continue
        
        frame = openCV.resize(
            frame, 
            (640, 640), 
            interpolation=openCV.INTER_CUBIC)
        y_max = frame.shape[0] - 50
        centro_cam = int((frame.shape[1] / 2)) - 60
        roi, contours, final = contourDetect(frame)
        openCV.circle(final, (centro_cam, y_max), 10, (0, 0, 255), -1)
        openCV.imshow("ROI", roi)
        #openCV.imshow("Original Image", img_reduce)
        openCV.imshow("Final Image", final)

        if openCV.waitKey(1) & 0xFF == ord('q'):
            break