from roverlib.exceptions import RoverLibError, HardwareNotAvailable


class CameraNotStart(RoverLibError, RuntimeError):
    """A câmera não foi iniciada: chame start() antes de capturar."""


class AutofocusModeInvalid(RoverLibError, RuntimeError):
    """O modo de autofoco atual não permite essa operação."""


class CameraNotAvailable(HardwareNotAvailable, ModuleNotFoundError):
    """picamera2/libcamera indisponíveis (PC). Herda de ModuleNotFoundError por compatibilidade."""
