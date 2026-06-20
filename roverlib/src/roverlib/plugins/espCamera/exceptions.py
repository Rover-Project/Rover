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
