from picamera2 import Picamera2
import cv2 as openCv
import numpy

class CircleDetect:
    def __init__(self, acumulado=25, minDist=200, minRadius=10, maxRadius=120):
        self.acumulado = acumulado
        self.minDist = minDist
        self.minRadius = minRadius
        self.maxRadius = maxRadius
        
        self.isCameraStart = False # Flag que indica se a config da camera ja foi feita
        
        # Cor que deve ser detectada
        self.color = {
            "low": numpy.array([115, 200, 100]),
            "high": numpy.array([130, 255, 255])
        }
        
        self.kernel = numpy.ones((5, 5), numpy.uint8) # mask de limpeza
        
    
    def cameraStart(self, h, w):
        self.camera = Picamera2()
        
        config = self.camera.create_preview_configuration(
            main={
                "format": "RGB888",
                "size": (h, w)
            }
        )
        
        self.camera.configure(config)
        self.camera.start() # Inicia a camera
        self.isCameraStart = True
        
    def cameraStop(self):
        self.camera.stop() # Para a camera
        self.isCameraStart = False
        
    def getCircle(self):
        if self.isCameraStart:
            frame = self.camera.capture_array()

            # Converter para HSV
            hsv = openCv.cvtColor(frame, openCv.COLOR_RGB2HSV)

            # Criar máscara da cor detectada pela câmera
            mask = openCv.inRange(hsv, self.color["low"], self.color["high"])

            # Limpar máscara
            mask = openCv.morphologyEx(mask, openCv.MORPH_OPEN, self.kernel)
            mask = openCv.morphologyEx(mask, openCv.MORPH_CLOSE, self.kernel)
            mask = openCv.GaussianBlur(mask, (9, 9), 2)

            # HoughCircles na máscara
            circles = openCv.HoughCircles(
                mask,
                openCv.HOUGH_GRADIENT,
                dp=1.2,
                minDist=self.minDist,
                param1=100,
                param2=self.acumulado,
                minRadius=self.minRadius,
                maxRadius=self.maxRadius
            )
            
            return circles, mask, frame
        else:
            raise RuntimeError("Inicie a camera primeiro!")
        
         