import cv2 as openCv
from time import time
from .cameraInterface import CameraInterface


class Webcam(CameraInterface):
    """
    Webcam (USB ou integrada ao PC), lida pelo OpenCV.

    Tem os mesmos métodos básicos da `Camera` (`get_frame()`, `start()`, `stop()`, `cleanup()`),
    por isso um programa escrito para o Rover roda no PC sem mudanças. Os frames vêm em BGR.
    A webcam começa a capturar ao ser criada; `start()` e `stop()` existem só por compatibilidade.
    """

    def __init__(self, height, width, fps: int = 30, index: int = 0):
        """
        Args:
            height (int): altura desejada dos frames (a webcam pode escolher o tamanho mais próximo).
            width (int): largura desejada dos frames.
            fps (int): quadros por segundo desejados. Padrão 30.
            index (int): qual webcam usar, se houver mais de uma. Padrão 0.
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
        Captura um frame.

        Returns:
            numpy.ndarray | None: imagem em BGR, ou None se a webcam não entregou um frame.
        """
        available, frame = self.camera.read()

        if available: # verifica se tem um frame disponivel
            return frame

        return None

    def get_frame_time(self):
        """
        Captura um frame e o instante da captura.

        Returns:
            tuple: `(frame, instante)`, com o instante em segundos (`time.time()`).
        """
        return self.get_frame(), time()

    def isRunning(self) -> bool:
        """
        Indica se a webcam está aberta.

        Returns:
            bool: True enquanto a webcam estiver disponível.
        """
        return self.camera.isOpened()

    def start(self):
        """Não faz nada: a webcam já captura desde a criação (existe por compatibilidade com `Camera`)."""
        pass

    def stop(self):
        """Não faz nada (existe por compatibilidade com `Camera`). Para liberar a webcam, use `cleanup()`."""
        pass

    def cleanup(self):
        """Libera a webcam."""
        self.camera.release() # libera o objeto camera
