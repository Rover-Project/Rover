from .motorInterface import MotorInterface

from .exceptions import (
    UninitializedMotorError, 
    DirectionInvalidMotorError,
)

class VirtualMotor(MotorInterface):
    """
        Classe para simulação do funcionamento de motores.
    """
    
    def __init__(self, pins: tuple[int, int], tag:str, pwm_frequency=1000):
        """
        Inicializa o driver para um motor.
        
        Args:
            pins: tupla com a indicação dos pinos da gpio que estão conectados nos entradas da ponte-H.
            pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 1000Hz)
        """
        
        self.pwm_frequency = pwm_frequency 
        self.in1, self.in2 = pins
        self._initialized = False # Flag que indica se os pinos já foram configurados
        self.name = tag
        
    def initialize(self):
        """Configura os pinos GPIO e inicia os sinais PWM."""
        if self._initialized:
            return
        
        self._initialized = True # Indica que os pinos foram cofigurados
        print(f"MotorDriver {self.name} inicializado. Frequência PWM: {self.pwm_frequency}Hz")
    
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
        
        speed = min(abs(speed), 100.0) # garante que o valor da velocidade está no intervalo [0,100]
        
        # Move para frente
        if direction == "FORWARD":
            print(f"{self.name}: Frente - velocidade: {speed}")
        
        # Move para trás
        elif direction == "BACKWARD":
            print(f"{self.name}: Trás - velocidade: {speed}")
            
        # Para 
        elif direction == "STOP":  
            print(f"{self.name}: Parado - velocidade: 0")
        
        # Acusa erro, pois a direção é inválida
        else:
            raise DirectionInvalidMotorError(
                "Direção de rotação para o motor inválida. A direção só pode ser: ['forward', 'backward', stop']"
            )
    
    def stop(self):
        """Para a rotação do motor"""
        self.set_movement(speed=0, direction="stop")
    
    def cleanup(self):
        """Libera recursos GPIO e para os motores."""
        if self._initialized:
            self.stop()
            self._initialized = False
            print(f"MotorDriver {self.name}: recursos liberados.")