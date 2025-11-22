"""
Driver para controle de motores via GPIO e PWM.
Responsável pela comunicação direta com o hardware da Raspberry Pi.
"""
import time
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (RuntimeError, ModuleNotFoundError):
    GPIO_AVAILABLE = False
    print("AVISO: RPi.GPIO não detectado. Este módulo requer Raspberry Pi com RPi.GPIO instalado.")
    raise ImportError("RPi.GPIO não está disponível. Execute este código na Raspberry Pi.")

from ...utils.constants import (
    MOTOR_ESQUERDO_IN1, MOTOR_ESQUERDO_IN2, MOTOR_ESQUERDO_ENA,
    MOTOR_DIREITO_IN3, MOTOR_DIREITO_IN4, MOTOR_DIREITO_ENB
)


class MotorDriver:
    """
    Driver de baixo nível para controle de motores DC via Ponte-H L298N.
    Gerencia pinos GPIO e sinais PWM diretamente.
    """
    
    def __init__(self, pwm_frequency=100):
        """
        Inicializa o driver de motores.
        
        Args:
            pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 100Hz)
        """
        if not GPIO_AVAILABLE:
            raise RuntimeError("GPIO não disponível. Execute na Raspberry Pi.")
        
        self.pwm_frequency = pwm_frequency
        self.pwm_esq = None
        self.pwm_dir = None
        self._initialized = False
        
    def initialize(self):
        """Configura os pinos GPIO e inicia os sinais PWM."""
        if self._initialized:
            return
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # Suprime avisos sobre pinos já configurados
        
        # configura pinos de direção
        GPIO.setup(MOTOR_ESQUERDO_IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR_ESQUERDO_IN2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR_DIREITO_IN3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR_DIREITO_IN4, GPIO.OUT, initial=GPIO.LOW)
        
        # configura os pinos PWM
        GPIO.setup(MOTOR_ESQUERDO_ENA, GPIO.OUT)
        GPIO.setup(MOTOR_DIREITO_ENB, GPIO.OUT)
        
        # inicializa objetos PWM
        self.pwm_esq = GPIO.PWM(MOTOR_ESQUERDO_ENA, self.pwm_frequency)
        self.pwm_dir = GPIO.PWM(MOTOR_DIREITO_ENB, self.pwm_frequency)
        self.pwm_esq.start(0)  # com 0% de duty cycle
        self.pwm_dir.start(0)
        
        self._initialized = True
        print(f"MotorDriver inicializado. Frequência PWM: {self.pwm_frequency}Hz")
    
    def set_motor_left(self, direction, speed):
        """
        Controla o motor esquerdo.
        
        Args:
            direction (str): 'forward', 'backward' ou 'stop'
            speed (float): Velocidade de 0 a 100 (duty cycle do PWM)
        """
        if not self._initialized:
            raise RuntimeError("Driver não inicializado. Chame initialize() primeiro.")
        
        speed = max(0, min(100, speed))  # normaliza de 0 a 100
        
        if direction == 'forward':
            GPIO.output(MOTOR_ESQUERDO_IN1, GPIO.HIGH)
            GPIO.output(MOTOR_ESQUERDO_IN2, GPIO.LOW)
            self.pwm_esq.ChangeDutyCycle(speed)
        elif direction == 'backward':
            GPIO.output(MOTOR_ESQUERDO_IN1, GPIO.LOW)
            GPIO.output(MOTOR_ESQUERDO_IN2, GPIO.HIGH)
            self.pwm_esq.ChangeDutyCycle(speed)
        else:  # stop
            GPIO.output(MOTOR_ESQUERDO_IN1, GPIO.LOW)
            GPIO.output(MOTOR_ESQUERDO_IN2, GPIO.LOW)
            self.pwm_esq.ChangeDutyCycle(0)
    
    def set_motor_right(self, direction, speed):
        """
        Controla o motor direito.
        
        Args:
            direction (str): 'forward', 'backward' ou 'stop'
            speed (float): Velocidade de 0 a 100 (duty cycle do PWM)
        """
        if not self._initialized:
            raise RuntimeError("Driver não inicializado. Chame initialize() primeiro.")
        
        speed = max(0, min(100, speed))  # normaliza de 0 a 100
        
        if direction == 'forward':
            GPIO.output(MOTOR_DIREITO_IN3, GPIO.HIGH)
            GPIO.output(MOTOR_DIREITO_IN4, GPIO.LOW)
            self.pwm_dir.ChangeDutyCycle(speed)
        elif direction == 'backward':
            GPIO.output(MOTOR_DIREITO_IN3, GPIO.LOW)
            GPIO.output(MOTOR_DIREITO_IN4, GPIO.HIGH)
            self.pwm_dir.ChangeDutyCycle(speed)
        else:  # parar
            GPIO.output(MOTOR_DIREITO_IN3, GPIO.LOW)
            GPIO.output(MOTOR_DIREITO_IN4, GPIO.LOW)
            self.pwm_dir.ChangeDutyCycle(0)
    
    def set_motors(self, left_direction, left_speed, right_direction, right_speed):
        """
        Controla ambos os motores simultaneamente.
        
        Args:
            left_direction (str): Direção do motor esquerdo
            left_speed (float): Velocidade do motor esquerdo (0-100)
            right_direction (str): Direção do motor direito
            right_speed (float): Velocidade do motor direito (0-100)
        """
        self.set_motor_left(left_direction, left_speed)
        self.set_motor_right(right_direction, right_speed)
    
    def stop_all(self):
        """Para ambos os motores imediatamente."""
        self.set_motors('stop', 0, 'stop', 0)
    
    def cleanup(self):
        """Libera recursos GPIO e para os motores."""
        if self._initialized:
            self.stop_all()
            if self.pwm_esq:
                self.pwm_esq.stop()
            if self.pwm_dir:
                self.pwm_dir.stop()
            GPIO.cleanup()
            self._initialized = False
            print("MotorDriver: recursos liberados.")

