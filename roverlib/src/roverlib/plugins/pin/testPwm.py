from pin import Pin
from pin import PinMode
import time

led = Pin(18, PinMode.PWM)

try:
    while True:

        print("PWM 10%")
        led.pwm(0.1)
        time.sleep(2)

        print("PWM 50%")
        led.pwm(0.5)
        time.sleep(2)

        print("PWM 90%")
        led.pwm(0.9)
        time.sleep(2)

except KeyboardInterrupt:
    print('Encerrando...')
    led.release()