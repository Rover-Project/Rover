"""
Comandos de alto nível para controle de movimento do Rover.
Fornece interface simplificada para operações comuns.
"""

import time

from roverlib.plugins.motor import motorDriver
from roverlib.plugins.motor.motorDriver import MotorDriver
from roverlib.plugins.motor.vitualMotor import VirtualMotor
from roverlib.utils.simulation import SIMULATE_ENV, resolve_simulate  # noqa: F401 (SIMULATE_ENV reexportado)
from .motorCalibration import Calibration


class Robot:
    """
    Comandos básicos de movimento do Rover.
    Fornece métodos intuitivos para controlar o movimento.

    Fora da Raspberry Pi (ou com simulate=True / ROVER_SIMULATE=1) os motores
    são simulados: os comandos são exibidos no terminal e nada é enviado à GPIO.
    """

    def __init__(
        self,
        right: tuple[int, int],
        left: tuple[int, int],
        calibration: Calibration = None,
        pwm_frequency: int = 1000,
        simulate: bool = None,
    ):
        """
        Inicia os drivers para os motores.
        Args:
            left (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da esquerda.
            right (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da direita.
            calibration (Calibration): Calibração para os motores. Por padrão Calibration(1, 1)
            pwm_frequency (int, optional): Frequência do sinal PWM em Hz(padrão: 1000Hz). Por padrão 1000.
            simulate (bool, optional):
                None (padrão) -> usa os motores reais se a GPIO estiver disponível; senão, simula.
                True -> sempre simula.
                False -> exige os motores reais (erro se a GPIO não estiver disponível).
        """

        simulate = resolve_simulate(
            simulate, motorDriver.PIN_AVAILABLE, "motores", "Robot(..., simulate=False)"
        )
        self.simulated = simulate

        # Crias instâncias para controlas os motores
        if simulate:
            self.left_motor = VirtualMotor(left, "esquerdo", pwm_frequency)
            self.right_motor = VirtualMotor(right, "direito", pwm_frequency)
        else:
            self.left_motor = MotorDriver(left, pwm_frequency)
            self.right_motor = MotorDriver(right, pwm_frequency)

        # Cada robô tem a sua própria calibração (evita compartilhar o objeto padrão)
        self.calibration = calibration if calibration is not None else Calibration(1, 1)

        # Inicias os motores
        self.left_motor.initialize()
        self.right_motor.initialize()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def forward(self, speed=50, duration=None):
        """
        Move o Rover para frente.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, move indefinidamente.
        """
        
        # calibra as velocidades
        right_speed, left_speed = self.calibration.get_calibration(speed, speed)  
        
        # Movimenta os motores para a frente
        self.left_motor.set_movement(left_speed)
        self.right_motor.set_movement(right_speed)
        
        # Delimita movimento por uma duração
        if duration is not None:
            time.sleep(duration)
            self.stop()
    
    def backward(self, speed=50, duration=None):
        """
        Move o Rover para trás.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, move indefinidamente.
        """
        
        # calibra as velocidades
        right_speed, left_speed = self.calibration.get_calibration(speed, speed)  
        
        # Movimenta os motores para a frente
        self.left_motor.set_movement(left_speed, "backward")
        self.right_motor.set_movement(right_speed, "backward")
        
        # Delimita movimento por uma duração
        if duration is not None:
            time.sleep(duration)
            self.stop()
    
    def turn_left(self, speed=50, duration=None):
        """
        Gira o Rover para a esquerda no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, gira indefinidamente.
        """
        
        self.left_motor.set_movement(speed, "backward")
        self.right_motor.set_movement(speed)
        
        # Delimita movimento por um intervalo de tempo
        if duration is not None:
            time.sleep(duration)
            self.stop()
    
    def turn_right(self, speed=50, duration=None):
        """
        Gira o Rover para a direita no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, gira indefinidamente.
        """
        
        self.left_motor.set_movement(speed)
        self.right_motor.set_movement(speed, "backward")
        
        # Delimita movimento por um intervalo de tempo
        if duration is not None:
            time.sleep(duration)
            self.stop()
    
    def move(self, speed_right:float, speed_left:float, duration=None):
        """
        Move os motores individualmente de acordo com a velocidade. 
        Velociade positiva indica rotação para frente.
        Velocidade negativa indica rotação para trás.
        
        Args:
            speed_right (float): Velocidade do motor direito.
            speed_left (float): _description_
            duration (_type_, optional): Duração do movimento. Se for None o movimento é por tempo indefinido.
        """
        
        # determina direção e velocidade para cada motor
        if speed_left > 0:
            left_dir = 'forward'
            left_speed = abs(speed_left)
        elif speed_left < 0:
            left_dir = 'backward'
            left_speed = abs(speed_left)
        else:
            left_dir = 'stop'
            left_speed = 0
        
        if speed_right > 0:
            right_dir = 'forward'
            right_speed = abs(speed_right)
            
        elif speed_right < 0:
            right_dir = 'backward'
            right_speed = abs(speed_right)
            
        else:
            right_dir = 'stop'
            right_speed = 0
        
        # Calibra as velocidades (get_calibration retorna na ordem: direita, esquerda)
        right_speed, left_speed = self.calibration.get_calibration(
            left_speed=left_speed, right_speed=right_speed
        )
        
        self.left_motor.set_movement(left_speed, left_dir)
        self.right_motor.set_movement(right_speed, right_dir)
        
        if duration is not None:
            time.sleep(duration)
            self.stop()

    def turn_degrees(self, degrees: float, time_to_turn: float = 12, turn_speed: float = 55):
        """
        Gira o robô no próprio eixo por uma quantidade de graus, estimada por tempo.
        Positivo para a direita, negativo para a esquerda.

        Args:
            degrees (float): ângulo do giro em graus (ex.: 90 ou -45).
            time_to_turn (float): tempo, em segundos, que o Rover leva para girar 360°
                na velocidade `turn_speed`. Meça no seu Rover para obter giros precisos.
            turn_speed (float): velocidade usada no giro (0 a 100).
        """
        turn_duration = abs(degrees) / 360 * time_to_turn

        if degrees > 0:
            self.turn_right(speed=turn_speed, duration=turn_duration)
        elif degrees < 0:
            self.turn_left(speed=turn_speed, duration=turn_duration)

    def stop(self):
        """Para o Rover imediatamente."""
        self.left_motor.stop()
        self.right_motor.stop()
    
    def cleanup(self):
        """Libera recursos do driver."""
        self.left_motor.cleanup()
        self.right_motor.cleanup()
