"""
Plugin PCAServos: servos ligados a um PCA9685 (I²C), com as bibliotecas da Adafruit.

    from roverlib.plugins.PCAServos import PCAServos, Servo, ContinuousServo, HARDWARE_AVAILABLE

As classes ficam em `pca9685/` (caminho antigo `roverlib.plugins.PCAServos.pca9685` continua válido).
Normalmente os servos da câmera são usados pelo PanTilt (rover.pan_tilt), não diretamente.
"""
from .pca9685 import (
    PCAServos, Servo, ContinuousServo, VirtualServo, VirtualContinuousServo,
    PCA_AVAILABLE, HARDWARE_AVAILABLE,
)
from .exceptions import PCANotAvailable, ServoAngleError

__all__ = [
    "PCAServos", "Servo", "ContinuousServo", "VirtualServo", "VirtualContinuousServo",
    "HARDWARE_AVAILABLE", "PCA_AVAILABLE", "PCANotAvailable", "ServoAngleError",
]
