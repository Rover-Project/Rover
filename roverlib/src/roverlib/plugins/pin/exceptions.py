from roverlib.exceptions import HardwareNotAvailable


class PinNotAvailable(HardwareNotAvailable):
    """O módulo nativo do plugin pin não pôde ser carregado (PC, ou versão de Python sem o .so compilado)."""
