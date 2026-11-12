from roverlib.exceptions import RoverLibError, HardwareNotAvailable


class PCANotAvailable(HardwareNotAvailable):
    """PCA9685 indisponível: bibliotecas da Adafruit/I²C ausentes ou placa não encontrada. Herda de RuntimeError."""


class ServoAngleError(RoverLibError, ValueError):
    """Ângulo fora do intervalo permitido para o servo (0° a 180°). Herda de ValueError."""
