from MotorCreatedError import MotorCreatedError


try:
    import RPi.GPIO as GPIO
    isGPIO = True
except:
    print("RPi.GPIO não disponível!")
    isGPIO = False


class Motor:
    """Controla um único motor com dois pinos IN1/IN2 via PWM."""
    def __init__(self, pins: tuple[int, int], pwm_freq=1000):
        if not isGPIO:
            raise MotorCreatedError("RPi.GPIO não importado!")

        self.in1, self.in2 = pins # Pinos da GPIO para a ponte-H
        self.pwm_freq = pwm_freq # Frequencia do pwm
        self.initialized = False # Indica se os pinos foram configurados ou nao

    # Configura os pinos da gpio
    def initialize(self):
        # Define os pinos como saida de corrente
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)

        # Configura os pinos como pinos pwm
        self.pwm1 = GPIO.PWM(self.in1, self.pwm_freq)
        self.pwm2 = GPIO.PWM(self.in2, self.pwm_freq)

        # Inicia o uso dos pinos
        self.pwm1.start(0)
        self.pwm2.start(0)

        # Sinaliza que os pinos foram configurados
        self.initialized = True

    # Define e muda a velocidade
    def set_speed(self, speed: float):
        """
        speed: -1.0 a 1.0
        positivo = frente
        negativo = trás
        """
        
        if not self.initialized:
            raise MotorCreatedError("Motor não inicializado!")

        # Limitar faixa
        speed = max(-1.0, min(1.0, speed))
        duty = abs(speed) * 100

        # Os pinos pwm nao podem ser ligados ao mesmo tempo, pois pode gerar curto circuito 
        if speed > 0:
            self.pwm1.ChangeDutyCycle(duty)
            self.pwm2.ChangeDutyCycle(0)
        elif speed < 0:
            self.pwm1.ChangeDutyCycle(0)
            self.pwm2.ChangeDutyCycle(duty)
        else:
            self.stop()

    # Para os motores
    def stop(self):
        if self.initialized:
            self.pwm1.ChangeDutyCycle(0)
            self.pwm2.ChangeDutyCycle(0)

    # Limpa os pinos
    def clear(self):
        self.stop()
        GPIO.cleanup([self.in1, self.in2])

