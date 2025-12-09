"""
Comandos de alto nível para controle de movimento do Rover.
Fornece interface simplificada para operações comuns.
"""
from .motor import Motor
from .motorCalibration import MotorCalibration

class Robot:
    """
    Comandos básicos de movimento do Rover.
    Fornece métodos intuitivos para controlar o movimento.
    """
    
    def __init__(self, left: tuple[int, int], right:tuple[int, int], pwm_frequency=1000):
        """
        Inicia os drivers para os motores.
        Args:
            left (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da esquerda.
            right (tuple[int, int]): Pinos da GPIO conectados a ponte-H para o motor da direita.
            pwm_frequency (int, optional): Frequência do sinal PWM em Hz(padrão: 1000Hz). Defaults to 1000.
        """
        
        # Crias instâncias para controlas os motores
        self.left_motor = Motor(left, pwm_frequency)
        self.right_motor = Motor(right, pwm_frequency)
        self.calibration = MotorCalibration() # Carrega os valores de calibracao do motores
        
        # Inicias os motores
        self.left_motor.initialize()
        self.right_motor.initialize()
    
    def forward(self, speed=50, duration=None):
        """
        Move o Rover para frente.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, move indefinidamente.
        
        Returns:
            bool: True se executado com sucesso
        """
        
        # Movimenta os motores para a frente
        self.left_motor.set_movement(speed)
        self.right_motor.set_movement(speed)
        
        # Delimita movimento por uma duração
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
        
        return True
    
    def backward(self, speed=50, duration=None):
        """
        Move o Rover para trás.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, move indefinidamente.
        
        Returns:
            bool: True se executado com sucesso
        """
        
        # Movimenta os motores para a frente
        self.left_motor.set_movement(speed, "backward")
        self.right_motor.set_movement(speed, "backward")
        
        # Delimita movimento por uma duração
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
        
        return True
    
    def turn_left(self, speed=50, duration=None):
        """
        Gira o Rover para a esquerda no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, gira indefinidamente.
        
        Returns:
            bool: True se executado com sucesso
        """
        
        self.left_motor.set_movement(speed, "backward")
        self.right_motor.set_movement(speed)
        
        # Delimita movimento por um intervalo de tempo
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
        
        return True
    
    def turn_right(self, speed=50, duration=None):
        """
        Gira o Rover para a direita no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, gira indefinidamente.
        
        Returns:
            bool: True se executado com sucesso
        """
        
        self.left_motor.set_movement(speed)
        self.right_motor.set_movement(speed, "backward")
        
        # Delimita movimento por um intervalo de tempo
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
        
        return True
    
    def move(self, speed_left, speed_right, calibration=False):
        """
        Controla os motores individualmente.
        
        Args:
            speed_left (float): Velocidade do motor esquerdo (-100 a 100)
                               Positivo = frente, Negativo = trás
            speed_right (float): Velocidade do motor direito (-100 a 100)
                                Positivo = frente, Negativo = trás
            calibration: Aplicar calibração nos motores
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
            
        if calibration:
            left_speed, right_speed = self.calibration.getCalibration(left_speed=left_speed, right_speed=right_speed) # Calibra as velocidades
        
        self.left_motor.set_movement(left_speed, left_dir)
        self.right_motor.set_movement(right_speed, right_dir)
    
    def stop(self):
        """Para o Rover imediatamente."""
        self.left_motor.stop()
        self.right_motor.stop()
    
    def cleanup(self):
        """Libera recursos do driver."""
        self.left_motor.cleanup()
        self.right_motor.cleanup()

