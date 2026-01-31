import cv2
import numpy as np

from rover.modules.camera.base import CameraModule
from rover.modules.camera.frame import Frame

try:
    from picamera2 import Picamera2
except (ImportError, ModuleNotFoundError):
    Picamera2 = None


class PiCamera2(CameraModule):

    def __init__(
        self,
        width: int,
        height: int,
        analogue_gain: float = 1.5,
        exposure_time: int = 30000,
        light_config: bool = False,
    ):
        if Picamera2 is None:
            raise RuntimeError("Picamera2 não disponível neste sistema")

        self.width = width
        self.height = height
        self.analogue_gain = analogue_gain
        self.exposure_time = exposure_time
        self.light_config = light_config
        self.picam2 = Picamera2()

    def start(self):
        config = self.picam2.create_preview_configuration(
            main={
                "size": (self.width, self.height),
                "format": "RGB888",
            }
        )

        if self.light_config:
            self.picam2.set_controls({
                "AnalogueGain": self.analogue_gain,
                "ExposureTime": self.exposure_time,
            })

        self.picam2.configure(config)
        self.picam2.start()

    def read(self) -> Frame:
        frame_rgb = self.picam2.capture_array("main")
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        return Frame.now(frame_bgr)

    def stop(self):
        self.picam2.stop()
