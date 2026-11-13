import logging
from typing import Optional

from roverlib.plugins.PCAServos.exceptions import PCANotAvailable, ServoAngleError

try:
    # Bibliotecas da Adafruit: só funcionam com I²C disponível (Raspberry Pi)
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
    PCA_AVAILABLE = True
except Exception:  # ImportError no PC; NotImplementedError/RuntimeError do Blinka sem I²C
    PCA_AVAILABLE = False

# Nome padrão dos plugins (PCA_AVAILABLE é mantido por compatibilidade)
HARDWARE_AVAILABLE = PCA_AVAILABLE

logger = logging.getLogger(__name__)

# Constantes padrão para servos RC a 50 Hz
_DEFAULT_FREQ_HZ = 50
_DEFAULT_MIN_PULSE = 500
_DEFAULT_MAX_PULSE = 2500


class PCAServos:
    """
    Interface de alto nível para controle de servos via módulo PCA9685.
    Utiliza as bibliotecas oficiais da Adafruit para resolver problemas de travamento.
    """
    
    def __init__(
        self,
        address: int = 0x40,
        bus: int = 1, # Mantido para compatibilidade, a Adafruit detecta o bus automaticamente via board
        frequency: float = _DEFAULT_FREQ_HZ,
    ) -> None:
        if not PCA_AVAILABLE:
            raise PCANotAvailable(
                "PCA9685 indisponível: as bibliotecas da Adafruit (I²C) não puderam ser carregadas. "
                "Este driver requer a Raspberry Pi; no PC, use os servos simulados."
            )
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(self.i2c, address=address)
            self.pca.frequency = frequency
            self.servos_instances = {}
            logger.info(f"PCAServos Adafruit iniciado | addr=0x{address:02X} freq={frequency} Hz")
        except Exception as e:
            raise PCANotAvailable(f"Falha ao inicializar o PCA9685 da Adafruit: {e}") from e

    def get_servo(self, channel: int, min_pulse: int = _DEFAULT_MIN_PULSE, max_pulse: int = _DEFAULT_MAX_PULSE):
        """Retorna a instância do servo Adafruit para o canal especificado."""
        if channel not in self.servos_instances:
            self.servos_instances[channel] = servo.Servo(
                self.pca.channels[channel],
                min_pulse=min_pulse,
                max_pulse=max_pulse
            )
        return self.servos_instances[channel]

    def close(self, keep_channels=()) -> None:
        """
        Fecha o barramento I2C e desliga os canais.

        Args:
            keep_channels: canais que continuam recebendo o sinal após o fechamento
                (o PCA9685 segue gerando o PWM sozinho). Útil para um servo de posição
                continuar segurando uma carga, como o TILT da câmera.
        """
        for channel, ch in self.servos_instances.items():
            if channel not in keep_channels:
                ch.fraction = None # Desliga o PWM
        self.pca.deinit()
        self.i2c.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return "PCAServos(Adafruit Backend)"


class Servo:
    """
    Abstração compatível com a sua interface antiga, mas que usa a Adafruit por trás.
    """
    def __init__(
        self,
        pca: PCAServos,
        channel: int,
        min_pulse_us: int = _DEFAULT_MIN_PULSE,
        max_pulse_us: int = _DEFAULT_MAX_PULSE,
    ) -> None:
        self._pca = pca
        self._channel = channel
        self._adafruit_servo = pca.get_servo(channel, min_pulse_us, max_pulse_us)

    @property
    def angle(self) -> Optional[float]:
        return self._adafruit_servo.angle

    @angle.setter
    def angle(self, degrees: float) -> None:
        degrees = float(degrees)
        if not (0.0 <= degrees <= 180.0):
            raise ServoAngleError(f"Ângulo inválido: {degrees}. O valor deve estar entre 0.0 e 180.0 graus para proteger o motor.")
        self._adafruit_servo.angle = degrees

    def detach(self) -> None:
        """Desativa o sinal PWM do servo (corta o torque)."""
        self._adafruit_servo.fraction = None

    def center(self) -> None:
        """Move o servo para o centro (90°)."""
        self.angle = 90.0

    def __repr__(self) -> str:
        return f"Servo Adafruit Wrapper(channel={self._channel})"


class ContinuousServo:
    """
    Abstração para servo de rotação contínua 360° usando a biblioteca Adafruit.
    """
    def __init__(
        self,
        pca: PCAServos,
        channel: int,
        min_pulse_us: int = _DEFAULT_MIN_PULSE,
        max_pulse_us: int = _DEFAULT_MAX_PULSE,
        neutral_pulse_us: int = 1500, # Mantido por compatibilidade
    ) -> None:
        self._pca = pca
        self._channel = channel
        # Cria um servo de rotação contínua da Adafruit
        if channel not in pca.servos_instances:
            pca.servos_instances[channel] = servo.ContinuousServo(
                pca.pca.channels[channel],
                min_pulse=min_pulse_us,
                max_pulse=max_pulse_us
            )
        self._adafruit_servo = pca.servos_instances[channel]

    @property
    def throttle(self) -> float:
        return self._adafruit_servo.throttle

    @throttle.setter
    def throttle(self, value: float) -> None:
        value = max(-1.0, min(1.0, float(value)))
        self._adafruit_servo.throttle = value

    def stop(self) -> None:
        """Para o servo."""
        self.throttle = 0.0

    def detach(self) -> None:
        """Desativa o sinal PWM."""
        self._adafruit_servo.fraction = None
