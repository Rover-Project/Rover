from pin import Pin
from pin import PinMode
import time

led = Pin(0, PinMode.PWM)

try:
    while True:

        print("PWM 10%")
        led.pwm(10)
        time.sleep(2)

        print("PWM 50%")
        led.pwm(50)
        time.sleep(2)

        print("PWM 90%")
        led.pwm(90)
        time.sleep(2)

except KeyboardInterrupt:
    led.release()