import cv2 as openCv 
import numpy

try:
    import picamera2 import Picamera2
except ModuleNotFoundError:
    print("Picamera2 não encontrado! Use na raspberry com uma camera conectada!")

class Camera:
    def __init__(self, h=640, w=480):
        self.camera = Picamera2() # Inicia camera
        
        camera_config = self.camera.create_preview_configuration(
            main={
                "format": "RGB888",
                "size": (h, w)
            }
        )
        
        self.camera.configure(camera_config) # Configura camera com as informacoes de camera_config
        self.camera.start()
        
    def getFrame(self):
        return self.camera.capture_array() # Captura um frame
    
    def grayFrame(self):
        frame = self.camera.capture_array() # Captura frame 
        
        return openCv.cvtColor(fram, cv2.COLOR_RGB2GRAY)
    
    def blur(self, frame):    
        return openCv.medianBlur(frame, 5) # blur para diminuir os ruido nas bordas
    
    def circleDetect(self, frame, minDist=40, minRadius=10, maxRadius=120):
        
        circles = openCv.HoughCircles(
            frame,
            openCv.HOUGH_GRADIENT,
            dp=1.2, # Razao de resolucao
            minDist=minDist, # Distancia minima entre centros
            param1=100, # Limite de Canny
            param2=30, # Limiar para detectar centro do circulo
            minRadius=minRadius, # Raio minimo
            maxRadius=maxRadius # Raio maximo
        )