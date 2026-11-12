from roverlib.exceptions import RoverLibError, HardwareNotAvailable


class LidarNotStart(RoverLibError, RuntimeError):
    """O Lidar não pôde ser iniciado (porta serial ausente, ocupada ou não iniciada)."""


class LidarDoNotRespond(RoverLibError, RuntimeError):
    """O Lidar foi iniciado, mas não envia dados (ligação incorreta ou falha de componente)."""


class LidarNotAvailable(HardwareNotAvailable, ModuleNotFoundError):
    """Biblioteca pyserial ausente. Herda de ModuleNotFoundError por compatibilidade."""
