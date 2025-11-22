"""
Comandos de alto nível para controle de movimento do Rover.
Fornece interface simplificada para operações comuns.
"""
from .driver import MotorDriver


class MovementCommands:
    """
    Comandos básicos de movimento do Rover.
    Fornece métodos intuitivos para controlar o movimento.
    """
    
    def __init__(self, driver=None, pwm_frequency=100):
        """
        Inicializa os comandos de movimento.
        
        Args:
            driver (MotorDriver, optional): Driver de motores. Se None, cria um novo.
            pwm_frequency (int): Frequência PWM (usado apenas se driver for None)
        """
        if driver is None:
            self.driver = MotorDriver(pwm_frequency=pwm_frequency)
        else:
            self.driver = driver
        
        self.driver.initialize()
    
    def forward(self, speed=50, duration=None):
        """
        Move o Rover para frente.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos. Se None, move indefinidamente.
        
        Returns:
            bool: True se executado com sucesso
        """
        self.driver.set_motors('forward', speed, 'forward', speed)
        
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
        self.driver.set_motors('backward', speed, 'backward', speed)
        
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
        self.driver.set_motors('backward', speed, 'forward', speed)
        
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
        self.driver.set_motors('forward', speed, 'backward', speed)
        
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
        
        return True
    
    def move(self, speed_left, speed_right):
        """
        Controla os motores individualmente.
        
        Args:
            speed_left (float): Velocidade do motor esquerdo (-100 a 100)
                               Positivo = frente, Negativo = trás
            speed_right (float): Velocidade do motor direito (-100 a 100)
                                Positivo = frente, Negativo = trás
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
        
        self.driver.set_motors(left_dir, left_speed, right_dir, right_speed)
    
    def stop(self):
        """Para o Rover imediatamente."""
        self.driver.stop_all()
    
    def cleanup(self):
        """Libera recursos do driver."""
        self.driver.cleanup()

