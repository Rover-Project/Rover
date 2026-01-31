from abc import ABC, abstractmethod

class MotorInterface(ABC):
    """
    Driver de baixo nível para controle de um motor DC via Ponte-H L298N.
    Gerencia pinos GPIO e sinais PWM diretamente.
    """
    
    @abstractmethod
    def __init__(self, pins: tuple[int, int], pwm_frequency=1000):
        """
            Inicializa o driver para um motor.
            
            Args:
                pins: tupla com a indicação dos pinos da gpio que estão conectados nos entradas da ponte-H.
                pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 1000Hz)
        """
        pass 
       
    
    @abstractmethod
    def initialize(self):
        """Configura os pinos GPIO e inicia os sinais PWM."""
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def stop(self):
        """Para a rotação do motor"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Libera recursos GPIO e para os motores."""
        pass