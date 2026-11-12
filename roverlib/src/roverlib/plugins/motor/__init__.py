"""
Plugin motor: controle de um motor DC por ponte-H L298N.

    from roverlib.plugins.motor import MotorDriver, VirtualMotor, HARDWARE_AVAILABLE

Normalmente os motores são usados pelo Robot (rover.move), não diretamente.
"""
from .motorInterface import MotorInterface
from .motorDriver import MotorDriver, HARDWARE_AVAILABLE
from .virtual import VirtualMotor
from .exceptions import DirectionInvalidMotorError, UninitializedMotorError, MotorCreationError

__all__ = [
    "MotorInterface", "MotorDriver", "VirtualMotor", "HARDWARE_AVAILABLE",
    "DirectionInvalidMotorError", "UninitializedMotorError", "MotorCreationError",
]
