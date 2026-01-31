class DirectionInvalidMotorError(Exception):
    """Direção inválida para a rotação dos motores."""
    pass

class UninitializedMotorError(Exception):
    """Motor não inicializado."""
    pass

class MotorCreationError(Exception):
    """GPIO não disponível."""
    pass