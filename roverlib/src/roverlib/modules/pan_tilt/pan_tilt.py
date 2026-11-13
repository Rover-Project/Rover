"""
Controle de alto nível do suporte pan-tilt da câmera.

No Rover:
    - PAN (horizontal): servo de rotação contínua (360°), controlado por velocidade e tempo.
      Como o servo não informa sua posição, o PanTilt a ESTIMA (velocidade × tempo) para
      respeitar os limites do giro (o cabo flat da câmera não pode ser forçado) e voltar
      a câmera para a frente.
    - TILT (vertical):  servo de posição (180°), controlado por ângulo.
Os dois ficam ligados a um PCA9685 (I²C). Fora da Raspberry Pi, os servos são simulados.
"""
import math
import threading
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
            camera_mount.pan_to(30)                  # gira até ~30° à direita
            camera_mount.pan_left(20, duration=0.3)  # gira para a esquerda por 0,3 s
            camera_mount.center()                    # volta a olhar para a frente

    Posição do PAN: 0° é a câmera olhando para a frente do Rover; positivo é a direita.
    O programa deve começar com a câmera de frente (o `cleanup()` a deixa assim ao terminar).

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
        pan_min: float = -50,
        pan_max: float = 50,
        pan_degrees_per_second=125,
        pan_calibration_speed: float = 20,
        pan_pulse: tuple = (500, 2500),
        tilt_pulse: tuple = (500, 2500),
        hold_tilt: bool = True,
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
            pan_min (float): limite do giro para a esquerda, em graus (negativo). None = sem limite.
            pan_max (float): limite do giro para a direita, em graus. None = sem limite.
            pan_degrees_per_second (float | tuple): graus por segundo que o PAN gira com a
                velocidade `pan_calibration_speed`. Um número vale para os dois sentidos;
                um par `(direita, esquerda)` corrige servos mais rápidos em um sentido.
                Meça no seu Rover: é o que torna a posição estimada confiável.
            pan_calibration_speed (float): velocidade (0 a 100) usada na medição acima.
                Também é a velocidade padrão de `pan_to()`, a mais precisa.
            pan_pulse (tuple): pulsos mínimo e máximo do servo PAN, em microssegundos.
            tilt_pulse (tuple): pulsos mínimo e máximo do servo TILT, em microssegundos.
            hold_tilt (bool): se True (padrão), o TILT continua segurando a câmera no centro
                depois do `cleanup()`. Sem sinal, o peso da câmera a faria cair.
            simulate (bool, optional):
                None (padrão) -> usa o PCA9685 se disponível; senão, simula.
                True -> sempre simula.
                False -> exige o hardware (erro se o PCA9685 não estiver disponível).
        """
        if not (0 <= tilt_min <= tilt_center <= tilt_max <= 180):
            raise ValueError("Os ângulos do TILT devem respeitar 0 <= tilt_min <= tilt_center <= tilt_max <= 180.")
        if (pan_min is not None and pan_min > 0) or (pan_max is not None and pan_max < 0):
            raise ValueError("Os limites do PAN devem respeitar pan_min <= 0 <= pan_max (0° = câmera de frente).")

        if isinstance(pan_degrees_per_second, (list, tuple)):
            rate_right, rate_left = pan_degrees_per_second
        else:
            rate_right = rate_left = pan_degrees_per_second
        if rate_right <= 0 or rate_left <= 0 or pan_calibration_speed <= 0:
            raise ValueError("pan_degrees_per_second e pan_calibration_speed devem ser positivos.")

        self.tilt_min = tilt_min
        self.tilt_max = tilt_max
        self.tilt_center = tilt_center
        self.tilt_invert = tilt_invert
        self.pan_trim = _clamp(pan_trim, -1.0, 1.0)
        self.pan_invert = pan_invert
        self.pan_min = -math.inf if pan_min is None else pan_min
        self.pan_max = math.inf if pan_max is None else pan_max
        self.pan_degrees_per_second = (rate_right, rate_left)
        self.pan_calibration_speed = pan_calibration_speed
        self.hold_tilt = hold_tilt
        self._tilt_channel = tilt_channel

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

        # Estado do PAN: posição estimada e o giro em andamento
        self._lock = threading.RLock()
        self._pan_position = 0.0
        self._pan_speed = 0.0
        self._pan_started = None    # instante em que o giro atual começou
        self._limit_timer = None    # para o giro sozinho ao chegar no limite
        self._tilt_angle = None
        self._closed = False
        self.stop_pan()

    # ---------- PAN (horizontal, rotação contínua) ----------

    def _rate(self, speed: float) -> float:
        """Graus por segundo estimados para uma velocidade (proporcional à medida de calibração)."""
        base = self.pan_degrees_per_second[0] if speed > 0 else self.pan_degrees_per_second[1]
        return base * abs(speed) / self.pan_calibration_speed

    def _update_position(self):
        """Soma à posição o quanto o PAN girou desde a última atualização."""
        if self._pan_started is None or self._pan_speed == 0:
            return
        now = time.monotonic()
        direction = 1 if self._pan_speed > 0 else -1
        moved = direction * self._rate(self._pan_speed) * (now - self._pan_started)
        self._pan_position = _clamp(self._pan_position + moved, self.pan_min, self.pan_max)
        self._pan_started = now

    def _cancel_limit_timer(self):
        if self._limit_timer is not None:
            self._limit_timer.cancel()
            self._limit_timer = None

    def pan(self, speed: float, duration: float = None):
        """
        Gira a câmera na horizontal. O giro para sozinho ao chegar em `pan_min`/`pan_max`.

        Args:
            speed (float): velocidade de -100 a 100. Positivo gira para a direita; negativo, para a esquerda.
            duration (float, optional): tempo em segundos. Se informado, espera e para o giro ao final.
                Sem duração, o PAN continua girando até `stop_pan()`, outro `pan()` ou o limite.
        """
        speed = _clamp(float(speed), -100.0, 100.0)

        with self._lock:
            self._update_position()
            self._cancel_limit_timer()
            if speed == 0:
                self.stop_pan()
                return

            direction = 1 if speed > 0 else -1
            limit = self.pan_max if direction > 0 else self.pan_min
            remaining = (limit - self._pan_position) * direction
            if remaining <= 0:
                self.stop_pan()     # já está no limite deste lado
                return
            time_to_limit = remaining / self._rate(speed)

            invert = -1 if self.pan_invert else 1
            self._pan.throttle = _clamp(self.pan_trim + invert * speed / 100.0, -1.0, 1.0)
            self._pan_speed = speed
            self._pan_started = time.monotonic()

            if duration is None and math.isfinite(time_to_limit):
                self._limit_timer = threading.Timer(time_to_limit, self.stop_pan)
                self._limit_timer.daemon = True
                self._limit_timer.start()

        if duration is not None:
            time.sleep(min(duration, time_to_limit))
            self.stop_pan()

    def pan_right(self, speed: float = 30, duration: float = None):
        """Gira a câmera para a direita (velocidade de 0 a 100)."""
        self.pan(abs(speed), duration)

    def pan_left(self, speed: float = 30, duration: float = None):
        """Gira a câmera para a esquerda (velocidade de 0 a 100)."""
        self.pan(-abs(speed), duration)

    def pan_to(self, angle: float, speed: float = None) -> float:
        """
        Gira a câmera até um ângulo estimado (0° = frente, positivo = direita).

        Args:
            angle (float): ângulo desejado. É limitado ao intervalo [pan_min, pan_max].
            speed (float, optional): velocidade do giro (0 a 100). Padrão: a de calibração.

        Returns:
            O ângulo de destino (após o limite).
        """
        speed = abs(self.pan_calibration_speed if speed is None else speed)
        target = _clamp(float(angle), self.pan_min, self.pan_max)
        delta = target - self.pan_position
        if speed == 0 or abs(delta) < 0.5:
            return target
        signed_speed = speed if delta > 0 else -speed
        self.pan(signed_speed, duration=abs(delta) / self._rate(signed_speed))
        with self._lock:
            self._pan_position = target   # evita acumular erro de arredondamento do tempo
        return target

    def pan_degrees(self, degrees: float, speed: float = None) -> float:
        """
        Gira a câmera por um ângulo aproximado, a partir da posição atual.
        Positivo para a direita, negativo para a esquerda.

        Returns:
            O ângulo de destino (após o limite).
        """
        if degrees == 0:
            return self.pan_position
        return self.pan_to(self.pan_position + degrees, speed)

    def stop_pan(self):
        """Para o giro horizontal."""
        with self._lock:
            self._update_position()
            self._cancel_limit_timer()
            self._pan.throttle = self.pan_trim
            self._pan_speed = 0.0
            self._pan_started = None

    def reset_pan_position(self, angle: float = 0.0):
        """
        Informa a posição real do PAN, corrigindo a estimativa.
        Use com a câmera parada, por exemplo após alinhá-la de frente (0°).
        """
        with self._lock:
            self._update_position()
            self._pan_position = float(angle)
            if self._pan_started is not None:
                self._pan_started = time.monotonic()

    @property
    def pan_position(self) -> float:
        """Ângulo estimado do PAN (0° = frente, positivo = direita)."""
        with self._lock:
            self._update_position()
            return self._pan_position

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
        """Volta a câmera para a frente: PAN em 0° (estimado) e TILT no centro."""
        self.pan_to(0)
        self.tilt_to(self.tilt_center, smooth=smooth)

    def stop(self):
        """Para o PAN (o TILT mantém a posição)."""
        self.stop_pan()

    def cleanup(self):
        """
        Centraliza a câmera e desliga os sinais. Pode ser chamado mais de uma vez.
        Com `hold_tilt=True`, o TILT continua segurando a câmera no centro.
        """
        if self._closed:
            return
        try:
            self.center()
        finally:
            self._closed = True
            try:
                self.stop_pan()
                self._pan.detach()
                if not self.hold_tilt:
                    self._tilt.detach()
            finally:
                if self._pca is not None:
                    keep = (self._tilt_channel,) if self.hold_tilt else ()
                    self._pca.close(keep_channels=keep)
                    self._pca = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def __repr__(self):
        modo = "simulado" if self.simulated else "PCA9685"
        return (f"PanTilt({modo}, pan={self.pan_position:.0f}°, tilt={self.tilt_angle:g}°, "
                f"pan_speed={self.pan_speed:g})")
