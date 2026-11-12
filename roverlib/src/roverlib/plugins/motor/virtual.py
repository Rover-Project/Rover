from .motorInterface import MotorInterface

from .exceptions import (
    UninitializedMotorError,
    DirectionInvalidMotorError,
)

_DIRECTION_NAMES = {"FORWARD": "Frente", "BACKWARD": "Trás", "STOP": "Parado"}


class VirtualMotor(MotorInterface):
    """
        Classe para simulação do funcionamento de motores.
        Usada automaticamente pelo Robot quando não há Raspberry Pi
        (ou quando o modo simulação é pedido).

        O estado atual fica disponível em `speed` e `direction`, o que
        permite testar programas sem o Rover.
    """

    def __init__(self, pins: tuple[int, int], tag: str = "motor", pwm_frequency=1000, verbose: bool = True):
        """
        Inicializa o driver para um motor.

        Args:
            pins: tupla com a indicação dos pinos da gpio que estão conectados nos entradas da ponte-H.
            tag (str): nome do motor, usado nas mensagens (ex.: "esquerdo").
            pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 1000Hz)
            verbose (bool): Se True, imprime no terminal quando o movimento do motor muda.
        """

        self.pwm_frequency = pwm_frequency
        self.in1, self.in2 = pins
        self._initialized = False # Flag que indica se os pinos já foram configurados
        self.name = tag
        self.verbose = verbose
        self.speed = 0.0 # Velocidade atual [0, 100]
        self.direction = "STOP" # Direção atual: FORWARD, BACKWARD ou STOP

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    def initialize(self):
        """Simula a configuração dos pinos GPIO e dos sinais PWM."""
        if self._initialized:
            return

        self._initialized = True # Indica que os pinos foram cofigurados
        self._log(f"[simulação] Motor {self.name} inicializado. Pinos: ({self.in1}, {self.in2})  Frequência PWM: {self.pwm_frequency}Hz")

    def set_movement(self, speed: float, direction="FORWARD"):
        """
        Controla o movimento dos motor.
        Args:
            speed (float): velociade de rotação que deve ser aplicada no motor.
            direction (str, optional): direção de rotação do motor. Defaults to "forward".
        Raises:
            UninitializedMotorError: Motor não foi inicializado.
            DirectionInvalidMotorError: Direção de rotação inválida.
        """

        # Faz um upper para evista erros de up case ou low case
        direction = direction.upper()

        if not self._initialized:
            raise UninitializedMotorError(
                "Motor não inicializado. Chame initialize() primeiro."
            )

        if direction not in _DIRECTION_NAMES:
            raise DirectionInvalidMotorError(
                "Direção de rotação para o motor inválida. A direção só pode ser: ['forward', 'backward', stop']"
            )

        speed = 0.0 if direction == "STOP" else min(abs(speed), 100.0) # garante que o valor da velocidade está no intervalo [0,100]

        # Só imprime quando o movimento muda, para não inundar o terminal em laços de controle
        if (speed, direction) != (self.speed, self.direction):
            self._log(f"[simulação] {self.name}: {_DIRECTION_NAMES[direction]} - velocidade: {speed:g}")

        self.speed = speed
        self.direction = direction

    def stop(self):
        """Para a rotação do motor"""
        self.set_movement(speed=0, direction="stop")

    def cleanup(self):
        """Libera recursos GPIO e para os motores."""
        if self._initialized:
            self.stop()
            self._initialized = False
            self._log(f"[simulação] Motor {self.name}: recursos liberados.")
