from rover.modules.movement.base import MotorDriver
from rover.modules.movement.exceptions import *
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class L298NMotor(MotorDriver):

    def __init__(self, pins: tuple[int, int], pwm_frequency=1000):
        if GPIO is None:
            raise RuntimeError("RPi.GPIO não disponível")

        self.in1, self.in2 = pins
        self.freq = pwm_frequency
        self.initialized = False

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)

        self.pwm1 = GPIO.PWM(self.in1, self.freq)
        self.pwm2 = GPIO.PWM(self.in2, self.freq)

        self.pwm1.start(0)
        self.pwm2.start(0)
        self.initialized = True

    def set(self, speed: float):
        speed = min(abs(speed), 100)

        if speed >= 0:
            self.pwm1.ChangeDutyCycle(speed)
            self.pwm2.ChangeDutyCycle(0)
        else:
            self.pwm1.ChangeDutyCycle(0)
            self.pwm2.ChangeDutyCycle(abs(speed))

    def stop(self):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)

    def cleanup(self):
        self.stop()
        GPIO.cleanup([self.in1, self.in2])
