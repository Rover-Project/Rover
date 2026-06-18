"""
pca9685/servos.py
=================
Abstração de alto nível para controle de servomotores via PCA9685.

Classes
-------
    PCAServos       : interface principal de controle (substitui adafruit_pca9685)
    Servo           : servo convencional 0°–180°
    ContinuousServo : servo de rotação contínua 360°

Referências de temporização (servos RC padrão)
-----------------------------------------------
    Frequência : 50 Hz  (período de 20 ms)
    Pulse mín  : ~0.5 ms → 2.5%  duty cycle → tick ≈  102  (neutro mín)
    Pulse neutro: ~1.5 ms → 7.5%  duty cycle → tick ≈  307
    Pulse máx  : ~2.5 ms → 12.5% duty cycle → tick ≈  512

    Conversão pulse → tick:
        tick = (pulse_ms / 20.0) × 4096

    Para ajuste fino, consulte o datasheet do servo utilizado.
"""

import logging
from typing import Optional

from .driver import PCA9685Driver, InvalidChannelError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes padrão para servos RC a 50 Hz
# ---------------------------------------------------------------------------
_DEFAULT_FREQ_HZ    = 50       # frequência padrão para servos
_DEFAULT_MIN_PULSE  = 500      # µs – pulse mínimo  (~0°  ou reverso máx)
_DEFAULT_MAX_PULSE  = 2500     # µs – pulse máximo  (~180° ou avanço máx)
_DEFAULT_NEUTRAL    = 1500     # µs – pulse neutro  (90°  ou parado)
_PERIOD_US          = 20_000   # µs – período a 50 Hz
_PWM_RESOLUTION     = 4096     # ticks por período (12 bits)


def _us_to_tick(pulse_us: int) -> int:
    """Converte largura de pulso em µs para tick (0–4095) a 50 Hz."""
    return round(pulse_us / _PERIOD_US * _PWM_RESOLUTION)


# ---------------------------------------------------------------------------
# PCAServos – interface principal
# ---------------------------------------------------------------------------
class PCAServos:
    """
    Interface de alto nível para controle de servos via PCA9685.

    Substitui a dependência da biblioteca adafruit_pca9685 mantendo
    compatibilidade com a interface existente no projeto.

    Parâmetros
    ----------
    frequency : float
        Frequência PWM em Hz. Padrão: 50 Hz (padrão para servos RC).
    address : int
        Endereço I2C do PCA9685. Padrão: 0x40.
    bus : int
        Barramento I2C da Raspberry Pi. Padrão: 1.

    Exemplo
    -------
    >>> servos = PCAServos(50)                      # só a frequência
    >>> servos.set_pwm(channel=0, on=0, off=307)     # posição neutra
    >>> servos.set_duty_cycle(channel=1, value=204)  # duty cycle baixo
    >>> servos.cleanup()

    Uso como context manager:
    >>> with PCAServos(50) as servos:
    ...     servos.set_pwm(0, 0, 307)
    """

    def __init__(
        self,
        frequency: float = _DEFAULT_FREQ_HZ,
        address: int = 0x40,
        bus: int = 1,
    ) -> None:
        self._driver = PCA9685Driver(address=address, bus=bus)
        self.set_frequency(frequency)
        logger.info(
            "PCAServos iniciado | addr=0x%02X bus=%d freq=%d Hz",
            address, bus, frequency,
        )

    # ------------------------------------------------------------------
    # Configuração de frequência
    # ------------------------------------------------------------------

    def set_frequency(self, frequency: float) -> None:
        """
        Configura a frequência PWM (afeta todos os canais).

        Para servos RC convencionais use 50 Hz.
        Para servos digitais, alguns aceitam até 333 Hz.

        Parâmetros
        ----------
        frequency : float
            Frequência em Hz (24–1526).
        """
        self._driver.set_frequency(frequency)

    # ------------------------------------------------------------------
    # Controle de canais
    # ------------------------------------------------------------------

    def set_pwm(self, channel: int, on: int, off: int) -> None:
        """
        Configura diretamente os ticks ON e OFF de um canal.

        Compatível com a interface do adafruit_pca9685.PCA9685.channels.

        Parâmetros
        ----------
        channel : int  – canal (0–15)
        on  : int      – tick de início HIGH (0–4095)
        off : int      – tick de início LOW  (0–4095)
        """
        self._driver.set_pwm(channel, on, off)

    def set_duty_cycle(self, channel: int, value: int) -> None:
        """
        Define o duty cycle via valor absoluto (0–4095).

        Equivalente a set_pwm(channel, 0, value).

        Parâmetros
        ----------
        channel : int  – canal (0–15)
        value   : int  – tick de duty cycle (0 = 0%, 4095 = 100%)
        """
        self._driver.set_duty_cycle(channel, value)

    def set_duty_cycle_percent(self, channel: int, percent: float) -> None:
        """
        Define o duty cycle em percentual (0.0–100.0%).

        Parâmetros
        ----------
        channel : int   – canal (0–15)
        percent : float – ex.: 7.5 para 7.5% (neutro de servo a 50 Hz)
        """
        self._driver.set_duty_cycle_percent(channel, percent)

    def set_pulse_us(self, channel: int, pulse_us: int) -> None:
        """
        Controla o canal pela largura de pulso em microsegundos.

        Conversão automática de µs para tick baseada na frequência de 50 Hz.

        Parâmetros
        ----------
        channel  : int – canal (0–15)
        pulse_us : int – largura de pulso em µs (ex.: 1500 para neutro)
        """
        tick = _us_to_tick(pulse_us)
        self._driver.set_pwm(channel, 0, tick)
        logger.debug("Canal %d: %d µs → tick %d", channel, pulse_us, tick)

    def set_all_pwm(self, on: int, off: int) -> None:
        """
        Define ON e OFF para TODOS os 16 canais simultaneamente.

        Parâmetros
        ----------
        on  : int – tick HIGH (0–4095)
        off : int – tick LOW  (0–4095)
        """
        self._driver.set_all_pwm(on, off)

    def get_pwm(self, channel: int) -> tuple[int, int]:
        """
        Lê os valores ON e OFF atuais de um canal.

        Retorna
        -------
        tuple[int, int] : (on, off)
        """
        return self._driver.get_pwm(channel)

    def reset_channel(self, channel: int) -> None:
        """Zera o PWM de um canal (saída LOW)."""
        self._driver.reset_channel(channel)

    def reset_all_channels(self) -> None:
        """Zera todos os 16 canais."""
        self._driver.reset_all_channels()

    # ------------------------------------------------------------------
    # Movimento contínuo por canal(is) — interface estilo motor
    # ------------------------------------------------------------------
    # Estes métodos tratam o(s) canal(is) informado(s) como servos de
    # rotação contínua (360°), controlados por uma porcentagem de
    # velocidade (0–100) em vez de throttle (-1.0 a 1.0). São úteis quando
    # o código que consome o módulo pensa em termos de "mover para frente/
    # para trás" (rodas, pan/tilt motorizado) em vez de ângulo absoluto.

    @staticmethod
    def _normalize_channels(channels) -> tuple:
        """Aceita um único canal (int) ou uma coleção de canais e
        sempre retorna uma tupla, para uso uniforme nos métodos abaixo."""
        if isinstance(channels, int):
            return (channels,)
        return tuple(channels)

    def forward(self, channels, speed: float = 100.0) -> None:
        """
        Move o(s) canal(is) informado(s) no sentido de avanço.

        Internamente, converte a porcentagem de velocidade em throttle
        positivo (0.0 a 1.0) e aplica via pulso PWM equivalente.

        Parâmetros
        ----------
        channels : int | tuple[int, ...]
            Canal único ou coleção de canais (0–15).
        speed : float
            Velocidade de 0 a 100 (%). Padrão: 100 (velocidade máxima).
        """
        speed = max(0.0, min(100.0, float(speed)))
        throttle = speed / 100.0
        pulse_us = round(
            _DEFAULT_NEUTRAL + throttle * (_DEFAULT_MAX_PULSE - _DEFAULT_NEUTRAL)
        )
        for ch in self._normalize_channels(channels):
            self.set_pulse_us(ch, pulse_us)
        logger.debug("forward(channels=%s, speed=%.1f%%)", channels, speed)

    def backward(self, channels, speed: float = 100.0) -> None:
        """
        Move o(s) canal(is) informado(s) no sentido reverso.

        Parâmetros
        ----------
        channels : int | tuple[int, ...]
            Canal único ou coleção de canais (0–15).
        speed : float
            Velocidade de 0 a 100 (%). Padrão: 100 (velocidade máxima).
        """
        speed = max(0.0, min(100.0, float(speed)))
        throttle = -(speed / 100.0)
        pulse_us = round(
            _DEFAULT_NEUTRAL + throttle * (_DEFAULT_NEUTRAL - _DEFAULT_MIN_PULSE)
        )
        for ch in self._normalize_channels(channels):
            self.set_pulse_us(ch, pulse_us)
        logger.debug("backward(channels=%s, speed=%.1f%%)", channels, speed)

    def stop(self, channels) -> None:
        """
        Para o(s) canal(is) informado(s), enviando o pulso neutro
        (sem desativar o sinal — o servo permanece "vivo", apenas parado).

        Parâmetros
        ----------
        channels : int | tuple[int, ...]
            Canal único ou coleção de canais (0–15).
        """
        for ch in self._normalize_channels(channels):
            self.set_pulse_us(ch, _DEFAULT_NEUTRAL)
        logger.debug("stop(channels=%s)", channels)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Fecha o driver e o barramento I2C."""
        self._driver.close()

    def cleanup(self) -> None:
        """Alias de close(), para compatibilidade com código que espera
        esse nome (padrão comum em bibliotecas de GPIO/hardware)."""
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return f"PCAServos({self._driver!r})"


# ---------------------------------------------------------------------------
# Servo – servo convencional 0°–180°
# ---------------------------------------------------------------------------
class Servo:
    """
    Abstração para servo convencional (0°–180°).

    Controla o servo informando um ângulo em graus. Internamente converte
    o ângulo para a largura de pulso equivalente e delega ao PCAServos.

    Parâmetros
    ----------
    pca : PCAServos
        Instância do controlador PCA9685.
    channel : int
        Canal PWM ao qual o servo está conectado (0–15).
    min_pulse_us : int
        Largura de pulso para 0°  em µs. Padrão: 500.
    max_pulse_us : int
        Largura de pulso para 180° em µs. Padrão: 2500.

    Exemplo
    -------
    >>> pca = PCAServos()
    >>> cam_tilt = Servo(pca, channel=0)
    >>> cam_tilt.angle = 90    # centro
    >>> cam_tilt.angle = 0     # mínimo
    >>> cam_tilt.angle = 180   # máximo
    """

    def __init__(
        self,
        pca: PCAServos,
        channel: int,
        min_pulse_us: int = _DEFAULT_MIN_PULSE,
        max_pulse_us: int = _DEFAULT_MAX_PULSE,
    ) -> None:
        self._pca         = pca
        self._channel     = channel
        self._min_pulse   = min_pulse_us
        self._max_pulse   = max_pulse_us
        self._current_angle: Optional[float] = None

        # Verifica o canal antes de usar
        if not (0 <= channel <= 15):
            raise InvalidChannelError(f"Canal {channel} inválido.")

    @property
    def angle(self) -> Optional[float]:
        """Retorna o ângulo atual (em graus), ou None se não definido."""
        return self._current_angle

    @angle.setter
    def angle(self, degrees: float) -> None:
        """
        Move o servo para o ângulo especificado (0.0–180.0 graus).

        Parâmetros
        ----------
        degrees : float
            Ângulo desejado. Será limitado a 0–180.
        """
        degrees = max(0.0, min(180.0, float(degrees)))
        pulse_us = self._angle_to_pulse(degrees)
        self._pca.set_pulse_us(self._channel, pulse_us)
        self._current_angle = degrees
        logger.debug(
            "Servo ch%d: %.1f° → %d µs", self._channel, degrees, pulse_us
        )

    def _angle_to_pulse(self, degrees: float) -> int:
        """Converte ângulo para largura de pulso em µs por interpolação linear."""
        ratio = degrees / 180.0
        return round(self._min_pulse + ratio * (self._max_pulse - self._min_pulse))

    def detach(self) -> None:
        """Desativa o sinal PWM do servo (deixa de forçar posição)."""
        self._pca.reset_channel(self._channel)
        self._current_angle = None
        logger.debug("Servo ch%d: detached", self._channel)

    def center(self) -> None:
        """Move o servo para o centro (90°)."""
        self.angle = 90.0

    def __repr__(self) -> str:
        return (
            f"Servo(channel={self._channel}, "
            f"angle={self._current_angle}, "
            f"pulse={self._min_pulse}–{self._max_pulse} µs)"
        )


# ---------------------------------------------------------------------------
# ContinuousServo – servo de rotação contínua 360°
# ---------------------------------------------------------------------------
class ContinuousServo:
    """
    Abstração para servo de rotação contínua (360°).

    A velocidade e direção são controladas pela largura de pulso:
        • Pulso neutro (~1500 µs) → parado
        • Pulso < neutro           → rotação em um sentido
        • Pulso > neutro           → rotação no sentido oposto
        • throttle = -1.0          → máxima velocidade reversa
        • throttle =  0.0          → parado
        • throttle = +1.0          → máxima velocidade avanço

    Parâmetros
    ----------
    pca : PCAServos
        Instância do controlador PCA9685.
    channel : int
        Canal PWM ao qual o servo está conectado (0–15).
    min_pulse_us : int
        Pulso para velocidade máxima reversa. Padrão: 500 µs.
    max_pulse_us : int
        Pulso para velocidade máxima avanço.  Padrão: 2500 µs.
    neutral_pulse_us : int
        Pulso de parada. Padrão: 1500 µs.

    Exemplo
    -------
    >>> pca = PCAServos()
    >>> motor = ContinuousServo(pca, channel=1)
    >>> motor.throttle = 0.5   # 50% avanço
    >>> motor.throttle = -1.0  # velocidade máxima reversa
    >>> motor.stop()            # para o motor
    """

    def __init__(
        self,
        pca: PCAServos,
        channel: int,
        min_pulse_us: int  = _DEFAULT_MIN_PULSE,
        max_pulse_us: int  = _DEFAULT_MAX_PULSE,
        neutral_pulse_us: int = _DEFAULT_NEUTRAL,
    ) -> None:
        self._pca          = pca
        self._channel      = channel
        self._min_pulse    = min_pulse_us
        self._max_pulse    = max_pulse_us
        self._neutral      = neutral_pulse_us
        self._throttle: float = 0.0

        if not (0 <= channel <= 15):
            raise InvalidChannelError(f"Canal {channel} inválido.")

    @property
    def throttle(self) -> float:
        """Retorna o throttle atual (-1.0 a +1.0)."""
        return self._throttle

    @throttle.setter
    def throttle(self, value: float) -> None:
        """
        Define a velocidade/direção do servo contínuo.

        Parâmetros
        ----------
        value : float
            Throttle de -1.0 (reverso máx) a +1.0 (avanço máx).
            0.0 = parado.
        """
        value = max(-1.0, min(1.0, float(value)))
        pulse_us = self._throttle_to_pulse(value)
        self._pca.set_pulse_us(self._channel, pulse_us)
        self._throttle = value
        logger.debug(
            "ContinuousServo ch%d: throttle=%.2f → %d µs",
            self._channel, value, pulse_us,
        )

    def _throttle_to_pulse(self, value: float) -> int:
        """
        Mapeia throttle (-1.0–+1.0) para largura de pulso.

        Dois segmentos lineares: reverso (neutro→min) e avanço (neutro→max).
        """
        if value >= 0:
            return round(self._neutral + value * (self._max_pulse - self._neutral))
        else:
            return round(self._neutral + value * (self._neutral - self._min_pulse))

    def stop(self) -> None:
        """Para o servo (throttle = 0)."""
        self.throttle = 0.0

    def detach(self) -> None:
        """Desativa o sinal PWM (sem forçar parada)."""
        self._pca.reset_channel(self._channel)
        self._throttle = 0.0

    def __repr__(self) -> str:
        return (
            f"ContinuousServo(channel={self._channel}, "
            f"throttle={self._throttle:.2f})"
        )
