"""
Controle de alto nível do suporte pan-tilt da câmera.

No Rover:
    - PAN (horizontal): servo de rotação contínua (360°), controlado por velocidade e tempo.
    - TILT (vertical):  servo de posição (180°), controlado por ângulo.
Os dois ficam ligados a um PCA9685 (I²C). Fora da Raspberry Pi, os servos são simulados.
"""
import time

from roverlib.plugins.PCAServos.pca9685 import servos as pca_module
from roverlib.plugins.PCAServos.pca9685.virtual import VirtualServo, VirtualContinuousServo
from roverlib.utils.simulation import resolve_simulate


def _clamp(value, low, high):
    return max(low, min(high, value))


class PanTilt:
    """
    Movimenta a câmera do Rover.

    Exemplo:
        with PanTilt() as camera_mount:
            camera_mount.tilt_to(60)                 # inclina para 60°
            camera_mount.pan_right(30, duration=0.5) # gira para a direita por 0,5 s
            camera_mount.center()

    Pelo Rover, é acessado como `rover.pan_tilt`.
    """

    def __init__(
        self,
        pan_channel: int = 0,
        tilt_channel: int = 1,
        address: int = 0x40,
        tilt_min: float = 0,
        tilt_max: float = 180,
        tilt_center: float = 90,
        tilt_invert: bool = False,
        pan_trim: float = 0.0,
        pan_invert: bool = False,
        pan_time_per_turn: float = 2.0,
        pan_pulse: tuple = (500, 2500),
        tilt_pulse: tuple = (500, 2500),
        simulate: bool = None,
    ):
        """
        Args:
            pan_channel (int): canal do PCA9685 do servo PAN (360°). Padrão 0.
            tilt_channel (int): canal do PCA9685 do servo TILT (180°). Padrão 1.
            address (int): endereço I²C do PCA9685. Padrão 0x40.
            tilt_min (float): menor ângulo permitido do TILT (protege o suporte). Padrão 0.
            tilt_max (float): maior ângulo permitido do TILT. Padrão 180.
            tilt_center (float): ângulo do TILT com a câmera olhando para frente. Padrão 90.
            tilt_invert (bool): inverte o sentido do TILT, se `tilt_up()` abaixar a câmera.
            pan_trim (float): velocidade (-1.0 a 1.0) em que o servo PAN fica realmente parado.
                Ajuste se a câmera girar sozinha devagar após `stop_pan()`.
            pan_invert (bool): inverte o sentido do PAN, se `pan_right()` girar para a esquerda.
            pan_time_per_turn (float): segundos que o PAN leva para dar uma volta completa com
                velocidade 100. Usado por `pan_degrees()`; meça no seu Rover.
            pan_pulse (tuple): pulsos mínimo e máximo do servo PAN, em microssegundos.
            tilt_pulse (tuple): pulsos mínimo e máximo do servo TILT, em microssegundos.
            simulate (bool, optional):
                None (padrão) -> usa o PCA9685 se disponível; senão, simula.
                True -> sempre simula.
                False -> exige o hardware (erro se o PCA9685 não estiver disponível).
        """
        if not (0 <= tilt_min <= tilt_center <= tilt_max <= 180):
            raise ValueError("Os ângulos do TILT devem respeitar 0 <= tilt_min <= tilt_center <= tilt_max <= 180.")

        self.tilt_min = tilt_min
        self.tilt_max = tilt_max
        self.tilt_center = tilt_center
        self.tilt_invert = tilt_invert
        self.pan_trim = _clamp(pan_trim, -1.0, 1.0)
        self.pan_invert = pan_invert
        self.pan_time_per_turn = pan_time_per_turn

        self.simulated = resolve_simulate(
            simulate, pca_module.PCA_AVAILABLE, "servos", "PanTilt(..., simulate=False)"
        )

        self._pca = None
        if self.simulated:
            self._pan = VirtualContinuousServo(pan_channel, name="PAN")
            self._tilt = VirtualServo(tilt_channel, name="TILT")
        else:
            self._pca = pca_module.PCAServos(address=address)
            self._pan = pca_module.ContinuousServo(self._pca, pan_channel, *pan_pulse)
            self._tilt = pca_module.Servo(self._pca, tilt_channel, *tilt_pulse)

        self._pan_speed = 0.0
        self._tilt_angle = None
        self.stop_pan()

    # ---------- PAN (horizontal, rotação contínua) ----------

    def pan(self, speed: float, duration: float = None):
        """
        Gira a câmera na horizontal.

        Args:
            speed (float): velocidade de -100 a 100. Positivo gira para a direita; negativo, para a esquerda.
            duration (float, optional): tempo em segundos. Se informado, para o giro ao final.
        """
        speed = _clamp(float(speed), -100.0, 100.0)
        direction = -1 if self.pan_invert else 1
        self._pan.throttle = _clamp(self.pan_trim + direction * speed / 100.0, -1.0, 1.0)
        self._pan_speed = speed

        if duration is not None:
            time.sleep(duration)
            self.stop_pan()

    def pan_right(self, speed: float = 30, duration: float = None):
        """Gira a câmera para a direita (velocidade de 0 a 100)."""
        self.pan(abs(speed), duration)

    def pan_left(self, speed: float = 30, duration: float = None):
        """Gira a câmera para a esquerda (velocidade de 0 a 100)."""
        self.pan(-abs(speed), duration)

    def pan_degrees(self, degrees: float, speed: float = 30):
        """
        Gira a câmera por um ângulo aproximado, estimado por tempo.
        Positivo para a direita, negativo para a esquerda.

        O servo de 360° não informa sua posição: a precisão depende de
        `pan_time_per_turn` estar medido para o seu Rover.

        Args:
            degrees (float): ângulo do giro em graus.
            speed (float): velocidade do giro (0 a 100).
        """
        if degrees == 0 or speed == 0:
            return
        # Tempo de uma volta na velocidade pedida (proporcional ao inverso da velocidade)
        time_per_turn = self.pan_time_per_turn * 100.0 / abs(speed)
        duration = abs(degrees) / 360.0 * time_per_turn
        self.pan(abs(speed) if degrees > 0 else -abs(speed), duration)

    def stop_pan(self):
        """Para o giro horizontal."""
        self._pan.throttle = self.pan_trim
        self._pan_speed = 0.0

    @property
    def pan_speed(self) -> float:
        """Velocidade atual do PAN (-100 a 100)."""
        return self._pan_speed

    # ---------- TILT (vertical, posição) ----------

    def tilt_to(self, angle: float, smooth: bool = False, step: float = 2, delay: float = 0.02):
        """
        Inclina a câmera para um ângulo.

        Args:
            angle (float): ângulo desejado. É limitado ao intervalo [tilt_min, tilt_max].
            smooth (bool): se True, move aos poucos em vez de saltar direto.
            step (float): tamanho de cada passo do movimento suave, em graus.
            delay (float): pausa entre os passos do movimento suave, em segundos.

        Returns:
            O ângulo aplicado (após o limite).
        """
        target = _clamp(float(angle), self.tilt_min, self.tilt_max)

        if smooth and self._tilt_angle is not None and step > 0:
            current = self._tilt_angle
            direction = 1 if target > current else -1
            while abs(target - current) > step:
                current += direction * step
                self._apply_tilt(current)
                time.sleep(delay)

        self._apply_tilt(target)
        return target

    def tilt_up(self, step: float = 10, smooth: bool = False):
        """Inclina a câmera para cima em `step` graus."""
        return self.tilt_to(self.tilt_angle + step, smooth=smooth)

    def tilt_down(self, step: float = 10, smooth: bool = False):
        """Inclina a câmera para baixo em `step` graus."""
        return self.tilt_to(self.tilt_angle - step, smooth=smooth)

    @property
    def tilt_angle(self) -> float:
        """Ângulo atual do TILT (o centro, se ainda não foi movido)."""
        return self.tilt_center if self._tilt_angle is None else self._tilt_angle

    def _apply_tilt(self, angle: float):
        self._tilt.angle = 180.0 - angle if self.tilt_invert else angle
        self._tilt_angle = angle

    # ---------- geral ----------

    def center(self, smooth: bool = False):
        """Para o PAN e coloca o TILT na posição central."""
        self.stop_pan()
        self.tilt_to(self.tilt_center, smooth=smooth)

    def stop(self):
        """Para o PAN (o TILT mantém a posição)."""
        self.stop_pan()

    def cleanup(self):
        """Para os servos e desliga os sinais. Pode ser chamado mais de uma vez."""
        try:
            self.stop_pan()
            self._pan.detach()
            self._tilt.detach()
        finally:
            if self._pca is not None:
                self._pca.close()
                self._pca = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def __repr__(self):
        modo = "simulado" if self.simulated else "PCA9685"
        return f"PanTilt({modo}, tilt={self.tilt_angle:g}°, pan_speed={self.pan_speed:g})"
