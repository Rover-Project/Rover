import cv2

from rover.modules.camera.base import CameraModule
from rover.modules.camera.frame import Frame


class Webcam(CameraModule):

    def __init__(self, width: int, height: int, device: int = 0):
        self.device = device
        self.width = width
        self.height = height
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cap.isOpened():
            raise RuntimeError("Não foi possível abrir a webcam")

    def read(self) -> Frame:
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Falha ao capturar frame da webcam")

        return Frame.now(frame)

    def stop(self):
        if self.cap:
            self.cap.release()
