"""
Driver para controle de motores via GPIO e PWM.
Responsável pela comunicação direta com o hardware da Raspberry Pi.
"""
from execeptions.motorExeceptions import (
    UninitializedMotorError, 
    DirectionInvalidMotorError, 
    MotorCreationError
)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (RuntimeError, ModuleNotFoundError):
    GPIO_AVAILABLE = False
    print("AVISO: RPi.GPIO não detectado. Este módulo requer Raspberry Pi com RPi.GPIO instalado.")
    raise ImportError("RPi.GPIO não está disponível. Execute este código na Raspberry Pi.")

class Motor:
    """
    Driver de baixo nível para controle de um motor DC via Ponte-H L298N.
    Gerencia pinos GPIO e sinais PWM diretamente.
    """
    
    def __init__(self, pins: tuple[int, int], pwm_frequency=1000):
        """
        Inicializa o driver para um motor.
        
        Args:
            pins: tupla com a indicação dos pinos da gpio que estão conectados nos entradas da ponte-H.
            pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 1000Hz)
        """
        
        if not GPIO_AVAILABLE:
            raise MotorCreationError("GPIO não disponível. Execute na Raspberry Pi.")
        
        self.pwm_frequency = pwm_frequency 
        self.in1, self.in2 = pins
        self._initialized = False # Flag que indica se os pinos já foram configurados
        
    def initialize(self):
        """Configura os pinos GPIO e inicia os sinais PWM."""
        if self._initialized:
            return
        
        GPIO.setmode(GPIO.BCM) # Indica que a númeração da GPIO deve ser Lógica
        GPIO.setwarnings(False)  # Suprime avisos sobre pinos já configurados
        
        # configura pinos como saida de sinal
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        
        # configura os pinos como pwm na frequencia correta
        self.pwm1 = GPIO.PWM(self.in1, self.pwm_frequency)
        self.pwm2 = GPIO.PWM(self.in2, self.pwm_frequency)
        
        # Inicia os pinos com 0 de dutycicle
        self.pwm1.start(0)
        self.pwm2.start(0)
        
        self._initialized = True # Indica que os pinos foram cofigurados
        print(f"MotorDriver inicializado. Frequência PWM: {self.pwm_frequency}Hz")
    
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
            self.pwm1.ChangeDutyCycle(speed) # Direciona um pulso com o valor de speed para o pwm1
            self.pwm2.ChangeDutyCycle(0) 
        
        # Move para trás
        elif direction == "BACKWARD":
            self.pwm1.ChangeDutyCycle(0)
            self.pwm2.ChangeDutyCycle(speed) # Direciona um pulso com o valor de speed para o pwm2
            
        # Para 
        elif direction == "STOP":  
            self.pwm1.ChangeDutyCycle(0)
            self.pwm2.ChangeDutyCycle(0)
        
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
            GPIO.cleanup([self.in1, self.in2])
            
            self._initialized = False
            print("MotorDriver: recursos liberados.")

