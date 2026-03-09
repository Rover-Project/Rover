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
        
        # duty para parar (cada servo pode variar um pouco)
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

    def stop(self):
        """Para o servo"""
        self.pwm.ChangeDutyCycle(self.stop_duty)

    def set_smooth_speed(self, init, end, step=0.05, time_step=0.05):
        """
        aceleração gradual
        """

        if init < end:
            speeds = [i * step for i in range(int(init/step), int(end/step))]
        else:
            speeds = [i * step for i in range(int(init/step), int(end/step), -1)]

        for speed in speeds:
            self.set_speed(speed)
            time.sleep(time_step)

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()