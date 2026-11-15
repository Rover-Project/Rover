"""
pin.py — Camada de abstração Python para controle GPIO (roverlib).

Importa o módulo nativo compilado (_pin_native, compilado na instalação) e expõe uma interface
Pythônica com nomes em português e validações adicionais.

Uso rápido
----------
from roverlib.plugins.pin import Pin, PinMode

led = Pin(17, PinMode.DIGITAL_OUT)
led.on()
led.off()
led.release()

servo = Pin(18, PinMode.PWM)          # hardware PWM
servo.pwm(0.075)                       # ~1,5 ms → posição central (50 Hz)
servo.pwm(0.05, frequency=50)          # explícito
servo.stop_pwm()
servo.release()
"""

from __future__ import annotations


import sys as _sys
import os as _os
from enum import IntEnum as _IntEnum

from .exceptions import PinNotAvailable

# Onde o módulo nativo (_pin_native) pode estar:
#   1. roverlib/plugins/pin/_pin_native*.so -> compilado pelo `pip install` na Raspberry Pi (normal)
#   2. roverlib/plugins/pin/bin/            -> compilado à mão com CMake (ver src/CMakeLists.txt)
_BIN_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bin")
if _BIN_DIR not in _sys.path:
    _sys.path.append(_BIN_DIR)

NATIVE_IMPORT_ERROR = None   # motivo da falha ao carregar o módulo nativo (diagnóstico)

try:
    try:
        from . import _pin_native as _native
    except ImportError:
        import _pin_native as _native
    HARDWARE_AVAILABLE = True
    # Re-exporta o enum nativo para que o usuário possa fazer `from roverlib.plugins.pin import PinMode`
    PinMode = _native.PinMode
except ImportError as _error:
    # PC, ou Raspberry Pi em que o módulo não foi compilado.
    # O módulo continua importável; criar um Pin gera PinNotAvailable.
    _native = None
    HARDWARE_AVAILABLE = False
    NATIVE_IMPORT_ERROR = _error

    class PinMode(_IntEnum):
        """Modos de operação do pino (substituto usado quando o módulo nativo não está disponível)."""
        DIGITAL_IN = 0
        DIGITAL_OUT = 1
        PWM = 2


def is_raspberry_pi() -> bool:
    """Indica se o código está rodando em uma Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", encoding="utf-8", errors="ignore") as f:
            return "raspberry pi" in f.read().lower()
    except OSError:
        return False


def _unavailable_message() -> str:
    """Explica por que a GPIO não está disponível e como resolver."""
    if not is_raspberry_pi():
        return ("O controle de GPIO só funciona na Raspberry Pi. "
                "No computador, use o modo simulação (o Robot e o Rover fazem isso sozinhos).")
    python = f"{_sys.version_info.major}.{_sys.version_info.minor}"
    return (
        f"O módulo nativo do plugin pin não foi compilado para este Python ({python}). "
        "Ele é compilado durante a instalação da RoverLib e precisa de um compilador C++ "
        "e dos cabeçalhos do Python. Para resolver, na pasta do repositório:\n"
        "    sudo apt install build-essential python3-dev\n"
        "    pip install -e roverlib --no-deps --force-reinstall -v\n"
        f"Erro original: {NATIVE_IMPORT_ERROR}"
    )


# Na Raspberry Pi, a falta do módulo nativo é um problema de instalação: avisa logo na importação,
# em vez de deixar o Robot cair na simulação sem explicação.
if not HARDWARE_AVAILABLE and is_raspberry_pi():
    import warnings as _warnings
    _warnings.warn(_unavailable_message(), RuntimeWarning, stacklevel=2)


def gpio_base() -> int:
    """
    Número do pino BCM 0 no sysfs (Pi 5: 571; Pi 4: 512), descoberto pelo módulo nativo.
    Pode ser forçado com a variável de ambiente ROVER_GPIO_BASE.
    """
    if not HARDWARE_AVAILABLE:
        raise PinNotAvailable(_unavailable_message())
    return _native.gpio_base()


class Pin:
    """
    Controla um pino GPIO da Raspberry Pi.

    Parâmetros
    ----------
    number : int
        Número BCM do pino (0–27).
    mode : PinMode
        Modo de operação: ``PinMode.DIGITAL_IN``, ``PinMode.DIGITAL_OUT``
        ou ``PinMode.PWM``.

    Exemplos
    --------
    Saída digital::

        led = Pin(17, PinMode.DIGITAL_OUT)
        led.on()
        led.off()
        led.release()

    PWM hardware (servo)::

        servo = Pin(18, PinMode.PWM)
        servo.pwm(0.075)          # posição central (50 Hz padrão)
        servo.pwm(0.05, 50)       # duty + frequência explícitos
        servo.stop_pwm()
        servo.release()

    PWM software (qualquer pino DIGITAL_OUT)::

        motor = Pin(17, PinMode.DIGITAL_OUT)
        motor.pwm(0.5, 1000)      # 50 % duty, 1 kHz
        motor.stop_pwm()
        motor.release()
    """

    def __init__(self, number: int, mode: PinMode) -> None:
        if not HARDWARE_AVAILABLE:
            raise PinNotAvailable(_unavailable_message())
        self._pin = _native.Pin(number, mode)

    # ------------------------------------------------------------------ #
    #  Interface Digital                                                   #
    # ------------------------------------------------------------------ #

    def on(self) -> None:
        """Coloca o pino em nível alto (HIGH). Requer modo DIGITAL_OUT."""
        self._pin.write(1)

    def off(self) -> None:
        """Coloca o pino em nível baixo (LOW). Requer modo DIGITAL_OUT."""
        self._pin.write(0)

    def write(self, value: int) -> None:
        """
        Escreve um valor digital no pino.

        Parâmetros
        ----------
        value : int
            ``0`` (LOW) ou ``1`` (HIGH).
        """
        self._pin.write(value)

    def read(self) -> int:
        """
        Lê o valor digital do pino.

        Retorna
        -------
        int
            ``0`` ou ``1``.
        """
        return self._pin.read()

    # ------------------------------------------------------------------ #
    #  Interface PWM                                                       #
    # ------------------------------------------------------------------ #

    def pwm(self, duty: float, frequency: float = 50.0) -> None:
        """
        Configura e inicia o sinal PWM.

        Parâmetros
        ----------
        duty : float
            Ciclo de trabalho entre ``0.0`` (0 %) e ``1.0`` (100 %).
        frequency : float, opcional
            Frequência em Hz (padrão: ``50.0``).

        Exemplos
        --------
        Servo motor (período de 20 ms)::

            servo.pwm(0.05)    # 1 ms  → posição mínima
            servo.pwm(0.075)   # 1,5 ms → posição central
            servo.pwm(0.10)    # 2 ms  → posição máxima

        ESC / motor DC::

            motor.pwm(0.0)     # parado
            motor.pwm(0.5)     # 50 % de potência
            motor.pwm(1.0)     # potência máxima
        """
        self._pin.pwmWrite(duty, frequency)

    def stop_pwm(self) -> None:
        """Para o sinal PWM sem liberar o pino."""
        self._pin.pwmStop()

    # ------------------------------------------------------------------ #
    #  Liberação                                                           #
    # ------------------------------------------------------------------ #

    def release(self) -> None:
        """Libera o pino do sysfs e encerra quaisquer threads ativas."""
        self._pin.release()

    # ------------------------------------------------------------------ #
    #  Propriedades informativas                                           #
    # ------------------------------------------------------------------ #

    @property
    def duty(self) -> float:
        """Duty cycle atual (0.0–1.0)."""
        return self._pin.getDuty()

    @property
    def frequency(self) -> float:
        """Frequência PWM atual em Hz."""
        return self._pin.getFrequency()

    @property
    def mode(self) -> PinMode:
        """Modo de operação configurado."""
        return self._pin.getMode()

    @property
    def number(self) -> int:
        """Número BCM do pino."""
        return self._pin.getPinNumber()

    @property
    def active(self) -> bool:
        """``True`` se o pino está inicializado e não foi liberado."""
        return self._pin.isActive()

    # ------------------------------------------------------------------ #
    #  Context manager (with statement)                                    #
    # ------------------------------------------------------------------ #

    def __enter__(self) -> "Pin":
        return self

    def __exit__(self, *_) -> None:
        self.release()

    # ------------------------------------------------------------------ #
    #  Representação                                                       #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return repr(self._pin)
