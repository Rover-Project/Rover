"""
Plugin camera: captura de imagens.

    from roverlib.plugins.camera import open_camera, Camera, AfCamera, Webcam, HARDWARE_AVAILABLE

- Camera / AfCamera: câmera da Raspberry Pi (picamera2); AfCamera controla o foco (Camera Module 3).
- Webcam: webcam do PC ou câmera USB (OpenCV); é a "versão de PC" deste plugin.
- open_camera(): escolhe automaticamente entre Camera e Webcam.
"""
from .cameraInterface import CameraInterface
from .camera import Camera, CameraFormat, HARDWARE_AVAILABLE
from .autoFocus import AfCamera, AfModeEnum, AfSpeedEnum
from .webcam import Webcam
from .factory import open_camera, picamera_available
from .exceptions import CameraNotStart, AutofocusModeInvalid, CameraNotAvailable

__all__ = [
    "open_camera", "picamera_available", "CameraInterface", "Camera", "CameraFormat",
    "AfCamera", "AfModeEnum", "AfSpeedEnum", "Webcam", "HARDWARE_AVAILABLE",
    "CameraNotStart", "AutofocusModeInvalid", "CameraNotAvailable",
]
