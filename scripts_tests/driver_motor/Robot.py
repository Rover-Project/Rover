from Motor import Motor
from MotorCreatedError import MotorCreatedError

try:
    import RPi.GPIO as GPIO
    isGPIO = True
except:
    print("RPi.GPIO não disponível!")
    isGPIO = False


class Robot:
    def __init__(self, left: tuple[int, int], right: tuple[int, int], pwm_freq=1000):
        if not isGPIO:
            raise MotorCreatedError("RPi.GPIO não importado!")

        self.left_motor = Motor(left, pwm_freq)
        self.right_motor = Motor(right, pwm_freq)

        GPIO.setmode(GPIO.BCM)

        self.left_motor.initialize()
        self.right_motor.initialize()

        self._value = (0.0, 0.0)  # (left_speed, right_speed)

    @property
    def value(self):
        return self._value

    def _apply(self, left_speed, right_speed):
        self.left_motor.set_speed(left_speed)
        self.right_motor.set_speed(right_speed)
        self._value = (left_speed, right_speed)

    def forward(self, speed=1.0):
        self._apply(speed, speed)

    def backward(self, speed=1.0):
        self._apply(-speed, -speed)

    def left(self, speed=1.0):
        self._apply(-speed, speed)

    def right(self, speed=1.0):
        self._apply(speed, -speed)

    def stop(self):
        self._apply(0.0, 0.0)

    def clear(self):
        self.left_motor.clear()
        self.right_motor.clear()