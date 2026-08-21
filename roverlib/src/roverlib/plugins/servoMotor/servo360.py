"""
Driver para servo de rotação contínua (360°) usando PWM no Raspberry Pi.
Controle baseado em velocidade e direção.
"""

import time

try:
    import RPi.GPIO as GPIO # type: ignore
    GPIO_AVAILABLE = True
    
except (RuntimeError, ModuleNotFoundError):
    GPIO_AVAILABLE = False
    print("AVISO: RPi.GPIO não detectado. Este módulo requer Raspberry Pi com RPi.GPIO instalado.")


class Servo360:

    def __init__(self, pin, frenquency=50, stop_duty=7.5, speed_range=1.0):
        self.pin = pin
        self.frenquency = frenquency
        
        # duty para parar
        self.stop_duty = stop_duty
        
        # quanto o duty varia para velocidade máxima
        self.speed_range = speed_range

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)

    def start(self):
        self.pwm = GPIO.PWM(self.pin, self.frenquency)
        self.pwm.start(self.stop_duty)

    def set_speed(self, speed):
        """
        speed: valor entre -1 e 1
        
        -1  -> máxima velocidade anti-horário
        0   -> parado
        1   -> máxima velocidade horário
        """

        speed = max(-1, min(1, speed))

        duty = self.stop_duty + speed * self.speed_range

        self.pwm.ChangeDutyCycle(duty)

    def mover_h(self, speed:float):
        self.set_speed(abs(speed))
    
    def mover_ant(self, speed:float):
        self.set_speed(-abs(speed))

    def stop(self):
        """Para o servo"""
        self.pwm.ChangeDutyCycle(self.stop_duty)
    

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()