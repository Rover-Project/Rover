from pin import Pin
from pin import PinMode
import time

led = Pin(18, PinMode.PWM)

try:

    while True:

        for duty in range(0, 101, 5):
            led.pwm(duty / 100)
            time.sleep(0.1)

        for duty in range(100, -1, -5):
            led.pwm(duty / 100)
            time.sleep(0.1)

finally:

    led.release()
