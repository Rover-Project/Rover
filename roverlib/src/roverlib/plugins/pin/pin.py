"""
pin.py — Camada de abstração Python para controle GPIO (roverlib).
"""

from __future__ import annotations

import _pin_native as _native  # importa o _pin_native.so compilado

# Re-exporta o enum para que o usuário possa fazer `from pin.pin import PinMode`
PinMode = _native.PinMode


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
        self._pin = _native.Pin(number, mode)

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
        value : int
            ``0`` (LOW) ou ``1`` (HIGH).
        """
        self._pin.write(value)

    def read(self) -> int:
        """
        Lê o valor digital do pino.

        Retorna
        int
            ``0`` ou ``1``.
        """
        return self._pin.read()

    def pwm(self, duty: float, frequency: float = 50.0) -> None:
        """
        Configura e inicia o sinal PWM.

        Parâmetros
        duty : float
            Ciclo de trabalho entre ``0.0`` (0 %) e ``1.0`` (100 %).
        frequency : float, opcional
            Frequência em Hz (padrão: ``50.0``).
        """
        self._pin.pwmWrite(duty, frequency)

    def stop_pwm(self) -> None:
        """Para o sinal PWM sem liberar o pino."""
        self._pin.pwmStop()

    def release(self) -> None:
        """Libera o pino do sysfs e encerra quaisquer threads ativas."""
        self._pin.release()

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

    def __enter__(self) -> "Pin":
        return self

    def __exit__(self, *_) -> None:
        self.release()

    def __repr__(self) -> str:
        return repr(self._pin)