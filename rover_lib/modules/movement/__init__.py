from .driver import MotorDriver
from .commands import MovementCommands
from .control import MovementControl, MotorCalibration

# mantém compatibilidade com código antigo
from .commands import MovementCommands as MovementModule

__all__ = [
    'MotorDriver',
    'MovementCommands',
    'MovementControl',
    'MotorCalibration',
    'MovementModule'
]

