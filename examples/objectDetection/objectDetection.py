
# Inicializando a câmera
import cv2

class ObjectDetection:
    def __init__(self , center_cam: float,):
        self.center_cam = center_cam

    def decision(self, coords, avoid_object: bool):
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2

        erro = x_center - self.center_cam

        if avoid_object:
            if erro > 20:
                print("Objeto fora de rota")
                return erro
            
            elif erro < 20:
                print("Objeto no caminho")
        
        else:
            if erro > 20:
                print("Objeto fora da rota. Corrigindo")

            elif erro < 20:
                print("Seguindo em direcao ao objeto")






