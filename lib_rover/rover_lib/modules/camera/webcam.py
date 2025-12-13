import cv2 as openCv
 
class Webcam:
    """
        Usa o webcam para ler frames
    """
    
    def __init__(self, height, width):
        self.camera = openCv.VideoCapture(0)
        self.camera.set(openCv.CAP_PROP_FRAME_HEIGHT, height) # definindo altura do frame
        self.camera.set(openCv.CAP_PROP_FRAME_WIDTH, width) # definindo largura
        
    def get_frame(self):
        ret, frame =  self.camera.read()
        return frame
    
    def cleanup(self):
        self.camera.release() # libera o objeto camera