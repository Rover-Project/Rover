import cv2 as openCv
from time import time
from .cameraInterface import CameraInterface


class Webcam(CameraInterface):
    """
        Usa uma webcam (USB ou integrada ao PC) para ler frames via OpenCV.
        Os frames são retornados no formato BGR.
    """

    def __init__(self, height, width, fps: int = 30, index: int = 0):
        """
        Args:
            height (int): altura dos frames
            width (int): largura dos frames
            fps (int, optional): taxa de quadros desejada. Valor padrão 30.
            index (int, optional): índice da webcam. Valor padrão 0.
        """
        self.size = (width, height)
        self.fps = fps
        self.index = index
        self.camera = openCv.VideoCapture(index)
        self.camera.set(openCv.CAP_PROP_FRAME_HEIGHT, height) # definindo altura do frame
        self.camera.set(openCv.CAP_PROP_FRAME_WIDTH, width) # definindo largura
        self.camera.set(openCv.CAP_PROP_FPS, fps)

    def get_frame(self):
        """
        Captura um único frame.

        Retorna:
            numpy.array (BGR) ou None se nenhum frame estiver disponível.
        """
        available, frame = self.camera.read()

        if available: # verifica se tem um frame disponivel
            return frame

        return None

    def get_frame_time(self):
        """
        Captura um frame e retorna o momento em que ele foi capturado
        Returns:
            (numpy array, time): tupla com o frame e o momento de captura.
        """
        return self.get_frame(), time()

    def isRunning(self) -> bool:
        """Retorna se a webcam está aberta."""
        return self.camera.isOpened()

    def start(self):
        pass

    def stop(self):
        pass

    def cleanup(self):
        self.camera.release() # libera o objeto camera
