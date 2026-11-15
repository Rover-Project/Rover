from roverlib.exceptions import HardwareNotAvailable


class PinNotAvailable(HardwareNotAvailable):
    """O módulo nativo do plugin pin não pôde ser carregado (PC, ou Raspberry Pi em que o módulo não foi compilado)."""
