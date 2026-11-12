"""
RoverLib: biblioteca educacional para controle do Rover.

Atalhos para as classes mais usadas:

    from roverlib import Rover, Robot, open_camera, Lidar, PID, ProcessingImage, VisionModule

As importações são feitas sob demanda, então `import roverlib` é rápido e não exige
OpenCV, câmera ou GPIO até que a classe correspondente seja usada.
"""
from importlib import import_module

__version__ = "0.1.0"

_EXPORTS = {
    "Rover": "roverlib.rover",
    "ComponentNotAvailable": "roverlib.rover",
    "Robot": "roverlib.modules.movement.robot",
    "Calibration": "roverlib.modules.movement.motorCalibration",
    "PID": "roverlib.modules.movement.PID",
    "open_camera": "roverlib.plugins.camera.factory",
    "Camera": "roverlib.plugins.camera.camera",
    "Webcam": "roverlib.plugins.camera.webcam",
    "Lidar": "roverlib.plugins.lidar.lidar",
    "ProcessingImage": "roverlib.modules.processing.processing_image",
    "VisionModule": "roverlib.modules.vision.visionModule",
    "Config": "roverlib.utils.config_manager",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name):
    if name in _EXPORTS:
        value = getattr(import_module(_EXPORTS[name]), name)
        globals()[name] = value  # guarda para os próximos acessos
        return value
    raise AttributeError(f"module 'roverlib' has no attribute '{name}'")


def __dir__():
    return sorted(list(globals()) + __all__)
