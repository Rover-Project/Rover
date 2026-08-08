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

class EspCamNotStart(RuntimeError):
    """
    Exceção caso a Esp Cam não seja iniciada em tempo tolerável
    """
    pass

class EspCamNotRespond(RuntimeError):
    """
    Exceção caso a câmera não responda por algum motivo qualquer.
    Args:
        RuntimeError (_type_): _description_
    """
    pass