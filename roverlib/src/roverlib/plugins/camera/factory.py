"""
Escolha automática da câmera: Picamera2 na Raspberry Pi, webcam no PC.
"""
from . import camera as _camera_module
from .camera import Camera
from .webcam import Webcam


def picamera_available() -> bool:
    """Indica se a câmera da Raspberry Pi (picamera2 + libcamera) pode ser usada."""
    return _camera_module.availablePicamera2 and _camera_module.availableLibcamera


def open_camera(height: int = 480, width: int = 640, fps: int = 30, index: int = 0,
                use_webcam: bool = None, **picamera_options):
    """
    Abre a câmera disponível e já a deixa pronta para capturar.

    Args:
        height (int): altura dos frames, em pixels. Padrão 480.
        width (int): largura dos frames, em pixels. Padrão 640.
        fps (int): quadros por segundo. Padrão 30.
        index (int): qual câmera usar, se houver mais de uma. Padrão 0.
        use_webcam (bool, optional): None (padrão) usa a Picamera2 se disponível e,
            senão, a webcam; True sempre usa a webcam (OpenCV); False exige a Picamera2.
        **picamera_options: opções extras da `Camera` (ex.: `horizontalFlip=True`,
            `verticalFlip=True`). Ignoradas quando a webcam é usada.

    Returns:
        Camera | Webcam: a câmera já iniciada. As duas têm `get_frame()` (frames em BGR),
            `start()`, `stop()` e `cleanup()`.

    Raises:
        CameraNotAvailable: `use_webcam=False` fora da Raspberry Pi.

    Exemplo:

    ```python
    cam = open_camera(480, 640)
    frame = cam.get_frame()
    cam.cleanup()
    ```
    """
    if use_webcam is None:
        use_webcam = not picamera_available()
        if use_webcam:
            print("AVISO: câmera da Raspberry Pi (picamera2) não disponível. Usando a webcam.")

    if use_webcam:
        cam = Webcam(height, width, fps=fps, index=index)
    else:
        cam = Camera(height, width, fps=fps, index=index, **picamera_options)

    cam.start()
    return cam
