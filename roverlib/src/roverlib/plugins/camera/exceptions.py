class CameraNotStart(RuntimeError):
    """
    Execeção caso a câmera não esteja inicializada.
    Args:
        RuntimeError (_type_): _description_
    """
    pass

class AutofocusModeInvalid(RuntimeError):
    """
    Execeção caso o mode de autofoco seja invalido para determinada operação
    """
    pass