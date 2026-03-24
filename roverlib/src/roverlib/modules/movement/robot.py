"""
Comandos de alto nível para controle de movimento do Rover.
Fornece interface simplificada para operações comuns.
"""
from roverlib.plugins.motor.motor import Motor
from .motorCalibration import Calibration
import time

class Robot:
    """
    Comandos básicos de movimento do Rover.
    Fornece métodos intuitivos para controlar o movimento.
    """
    
    def __init__(self, right:tuple[int, int], left: tuple[int, int], calibration: Calibration=Calibration(1, 1), pwm_frequency=1000):
        """
        Inicia os drivers para os motores.
        Args:
            left (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da esquerda.
            right (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da direita.
            calibration (Calibration): Calibração para os motores. Por padrão Calibration(1, 1)
            pwm_frequency (int, optional): Frequência do sinal PWM em Hz(padrão: 1000Hz). Por padrão 1000.
        """
        
        # Crias instâncias para controlas os motores
        self.left_motor = Motor(left, pwm_frequency)
        self.right_motor = Motor(right, pwm_frequency)
        self.calibration = calibration 
        
        # Inicias os motores
        self.left_motor.initialize()
        self.right_motor.initialize()
    
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
        
        left_speed, right_speed = self.calibration.get_calibration(
            left_speed=left_speed, right_speed=right_speed
        ) # Calibra as velocidades
        
        self.left_motor.set_movement(left_speed, left_dir)
        self.right_motor.set_movement(right_speed, right_dir)
        
        if duration is not None:
            time.sleep(duration)
            self.stop()

    # Considerando que o Rover leva x segundos para girar 360 graus em uma velocidade estabelecida
    def turn_degrees(self, degress: float, time_to_turn = 12, turn_speed=55): # Valores ainda nao testados
        """
        Gira o robô por uma quantidade específica de graus baseada em tempo.
        Positivo para Direita, Negativo para Esquerda.
        """
        turn_duration = abs(degress) * (360 / time_to_turn)
        print(turn_duration)
        if degress > 0:
            self.turn_right(speed=turn_speed, duration=turn_duration)
        else:
            self.turn_left(speed=turn_speed, duration=turn_duration)


    def stop(self):
        """Para o Rover imediatamente."""
        self.left_motor.stop()
        self.right_motor.stop()
    
    def cleanup(self):
        """Libera recursos do driver."""
        self.left_motor.cleanup()
        self.right_motor.cleanup()