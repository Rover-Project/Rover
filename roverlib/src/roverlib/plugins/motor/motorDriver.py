"""
    Driver de baixo nível para controle de um motor DC via Ponte-H L298N.
    Utiliza o plugin pin (C++/pybind11) no lugar do RPi.GPIO.
"""

from .motorInterface import MotorInterface
from .exceptions import UninitializedMotorError, DirectionInvalidMotorError, MotorCreationError

from roverlib.plugins.pin import Pin, PinMode
from roverlib.plugins.pin import HARDWARE_AVAILABLE

# Nome antigo, mantido por compatibilidade. Sem o plugin pin (PC ou versão de Python
# sem o .so compilado), o Robot usa esse indicador para cair no VirtualMotor.
PIN_AVAILABLE = HARDWARE_AVAILABLE


class MotorDriver(MotorInterface):
    """
    Controla um motor DC ligado a uma ponte-H L298N, pelo plugin `pin`.

    O motor é ligado a duas entradas da ponte-H (IN1/IN2 ou IN3/IN4). A velocidade é o
    ciclo de trabalho do PWM em uma delas; a outra fica em 0, e qual delas recebe o PWM
    define o sentido.

    Exemplo:

    ```python
    motor = MotorDriver(pins=(17, 26))
    motor.initialize()
    motor.set_movement(50, "FORWARD")
    motor.cleanup()
    ```

    Normalmente o motor é usado pelo `Robot`, que cria os dois motores e cai no
    `VirtualMotor` fora da Raspberry Pi.
    """

    def __init__(self, pins: tuple[int, int], pwm_frequency=1000):
        """
        Args:
            pins (tuple[int, int]): pinos GPIO (numeração BCM) ligados às duas entradas da ponte-H.
            pwm_frequency (int): frequência do PWM, em Hz. Padrão 1000.

        Raises:
            MotorCreationError: o plugin `pin` não está disponível (PC, ou módulo nativo não compilado).
        """
        if not PIN_AVAILABLE:
            raise MotorCreationError(
                "O plugin pin não está disponível. "
                "Compile o módulo C++ e execute na Raspberry Pi."
            )
        
        self.pwm_frequency = pwm_frequency
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
        """
        Gira o motor com uma velocidade e um sentido.

        Args:
            speed (float): velocidade de 0 a 100 (porcentagem do PWM). Valores acima de 100 são limitados.
            direction (str): `"FORWARD"` (frente), `"BACKWARD"` (trás) ou `"STOP"`. Aceita minúsculas. Padrão `"FORWARD"`.

        Raises:
            UninitializedMotorError: o motor não foi inicializado com `initialize()`.
            DirectionInvalidMotorError: sentido diferente dos três aceitos.
        """
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
        """Para o motor (as duas entradas em 0)."""
        self.set_movement(speed=0, direction="STOP")

    def cleanup(self):
        """Para o motor e libera os pinos GPIO. Pode ser chamado mais de uma vez."""
        if not self._initialized:
            return
        self.stop()
        self._pin1.release()
        self._pin2.release()
        self._pin1 = None
        self._pin2 = None
        self._initialized = False
        print("MotorDriver: recursos liberados.")