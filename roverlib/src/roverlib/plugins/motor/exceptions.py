from roverlib.exceptions import RoverLibError, HardwareNotAvailable


class DirectionInvalidMotorError(RoverLibError, ValueError):
    """Direção inválida para a rotação dos motores."""


class UninitializedMotorError(RoverLibError, RuntimeError):
    """Motor não inicializado: chame initialize() antes de movê-lo."""


class MotorCreationError(HardwareNotAvailable, ImportError):
    """GPIO não disponível (plugin pin ausente). Herda de ImportError por compatibilidade."""
