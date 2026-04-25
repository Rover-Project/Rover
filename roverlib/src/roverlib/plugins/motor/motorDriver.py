"""
    Driver de baixo nível para controle de um motor DC via Ponte-H L298N.
    Utiliza o plugin pin (C++/pybind11) no lugar do RPi.GPIO.
"""

from .motorInterface import MotorInterface
from .exceptions import UninitializedMotorError, DirectionInvalidMotorError

try:
    from roverlib.plugins.pin.pin import Pin, PinMode
    PIN_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PIN_AVAILABLE = False
    print("AVISO: plugin pin não detectado. Este módulo requer Raspberry Pi com o plugin compilado.")


class MotorDriver(MotorInterface):
    """
    Controla um único motor DC via Ponte-H L298N usando o plugin pin.
    """

    def __init__(self, pins: tuple[int, int], pwm_frequency=100):
        if not PIN_AVAILABLE:
            raise ImportError(
                "O plugin pin não está disponível. "
                "Compile o módulo C++ e execute na Raspberry Pi."
            )
        
        self.pwm_frequency = pwm_frequency
        
        print("Vasco da gama")
        
        print(f"Valor dos pins: {pins}")
        
        print("Vasco da gama")
                    
        self.in1, self.in2 = pins
        self._initialized = False
        self._pin1: Pin | None = None
        self._pin2: Pin | None = None

    def initialize(self):
        """Configura os pinos GPIO e inicia os sinais PWM."""
        if self._initialized:
            return
        self._pin1 = Pin(self.in1, PinMode.DIGITAL_OUT)
        self._pin2 = Pin(self.in2, PinMode.DIGITAL_OUT)
        self._pin1.pwm(0.0, self.pwm_frequency)
        self._pin2.pwm(0.0, self.pwm_frequency)
        self._initialized = True
        print(f"MotorDriver inicializado. Pinos: ({self.in1}, {self.in2})  Frequência PWM: {self.pwm_frequency} Hz")

    def set_movement(self, speed: float, direction="FORWARD"):
        if not self._initialized:
            raise UninitializedMotorError("Motor não inicializado. Chame initialize() primeiro.")

        direction = direction.upper()
        duty = min(abs(speed), 100.0) / 100.0

        if direction == "FORWARD":
            self._pin1.pwm(duty, self.pwm_frequency)
            self._pin2.pwm(0.0,  self.pwm_frequency)
        elif direction == "BACKWARD":
            self._pin1.pwm(0.0,  self.pwm_frequency)
            self._pin2.pwm(duty, self.pwm_frequency)
        elif direction == "STOP":
            self._pin1.pwm(0.0, self.pwm_frequency)
            self._pin2.pwm(0.0, self.pwm_frequency)
        else:
            raise DirectionInvalidMotorError(
                "Direção inválida. Use: 'FORWARD', 'BACKWARD' ou 'STOP'."
            )

    def stop(self):
        self.set_movement(speed=0, direction="STOP")

    def cleanup(self):
        if not self._initialized:
            return
        self.stop()
        self._pin1.release()
        self._pin2.release()
        self._pin1 = None
        self._pin2 = None
        self._initialized = False
        print("MotorDriver: recursos liberados.")