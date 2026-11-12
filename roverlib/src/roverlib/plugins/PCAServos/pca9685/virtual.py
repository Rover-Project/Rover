"""
Servos simulados, com a mesma interface de Servo e ContinuousServo.
Usados automaticamente fora da Raspberry Pi (ou quando a simulação é pedida).
"""
from typing import Optional

from roverlib.plugins.PCAServos.exceptions import ServoAngleError


class VirtualServo:
    """Simula um servo de posição (0° a 180°)."""

    def __init__(self, channel: int, name: str = "servo", verbose: bool = True) -> None:
        self._channel = channel
        self.name = name
        self.verbose = verbose
        self._angle: Optional[float] = None

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    @property
    def angle(self) -> Optional[float]:
        return self._angle

    @angle.setter
    def angle(self, degrees: float) -> None:
        degrees = float(degrees)
        if not (0.0 <= degrees <= 180.0):
            raise ServoAngleError(f"Ângulo inválido: {degrees}. O valor deve estar entre 0.0 e 180.0 graus para proteger o motor.")
        if degrees != self._angle:
            self._log(f"[simulação] {self.name} (canal {self._channel}): {degrees:g}°")
        self._angle = degrees

    def center(self) -> None:
        self.angle = 90.0

    def detach(self) -> None:
        self._log(f"[simulação] {self.name} (canal {self._channel}): sinal desligado")

    def __repr__(self) -> str:
        return f"VirtualServo(channel={self._channel})"


class VirtualContinuousServo:
    """Simula um servo de rotação contínua (360°), controlado por velocidade de -1.0 a 1.0."""

    def __init__(self, channel: int, name: str = "servo 360", verbose: bool = True) -> None:
        self._channel = channel
        self.name = name
        self.verbose = verbose
        self._throttle = 0.0

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    @property
    def throttle(self) -> float:
        return self._throttle

    @throttle.setter
    def throttle(self, value: float) -> None:
        value = max(-1.0, min(1.0, float(value)))
        if value != self._throttle:
            self._log(f"[simulação] {self.name} (canal {self._channel}): velocidade {value:+.2f}")
        self._throttle = value

    def stop(self) -> None:
        self.throttle = 0.0

    def detach(self) -> None:
        self._throttle = 0.0
        self._log(f"[simulação] {self.name} (canal {self._channel}): sinal desligado")

    def __repr__(self) -> str:
        return f"VirtualContinuousServo(channel={self._channel})"
