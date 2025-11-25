from .Motor import MotorDriver
from .robot import MovementCommands
from .control import MovementControl, MotorCalibration

# mantém compatibilidade com código antigo
from .robot import MovementCommands as MovementModule

__all__ = [
    'MotorDriver',
    'MovementCommands',
    'MovementControl',
    'MotorCalibration',
    'MovementModule'
]

