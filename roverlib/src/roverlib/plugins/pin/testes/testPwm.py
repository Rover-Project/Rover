from pin import Pin
from pin import PinMode
import time

led = Pin(12, PinMode.PWM)

try:
    while True:

        print("PWM 10%")
        led.pwm(0.1)
        time.sleep(1)

        print("PWM 20%")
        led.pwm(0.2)
        time.sleep(1)

        print("PWM 30%")
        led.pwm(0.3)
        time.sleep(1)

        print("PWM 40%")
        led.pwm(0.4)
        time.sleep(1)

        print("PWM 50%")
        led.pwm(0.5)
        time.sleep(1)

        print("PWM 60%")
        led.pwm(0.6)
        time.sleep(1)

        print("PWM 70%")
        led.pwm(0.7)
        time.sleep(1)

        print("PWM 80%")
        led.pwm(0.8)
        time.sleep(1)

        print("PWM 90%")
        led.pwm(0.9)
        time.sleep(1)

        print("PWM 100%")
        led.pwm(1)
        time.sleep(1)

except KeyboardInterrupt:
    print('Encerrando...')
    led.release()