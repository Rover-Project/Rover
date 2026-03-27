from pin import Pin
from pin import PinMode
import time

led = Pin(17, PinMode.PWM)

try:
    while True:

        print("PWM 10%")
        led.pwmWrite(0.1)
        time.sleep(1)

        print("PWM 20%")
        led.pwmWrite(0.2)
        time.sleep(1)

        print("PWM 30%")
        led.pwmWrite(0.3)
        time.sleep(1)

        print("PWM 40%")
        led.pwmWrite(0.4)
        time.sleep(1)

        print("PWM 50%")
        led.pwmWrite(0.5)
        time.sleep(1)

        print("PWM 60%")
        led.pwmWrite(0.6)
        time.sleep(1)

        print("PWM 70%")
        led.pwmWrite(0.7)
        time.sleep(1)

        print("PWM 80%")
        led.pwmWrite(0.8)
        time.sleep(1)

        print("PWM 90%")
        led.pwmWrite(0.9)
        time.sleep(1)

        print("PWM 100%")
        led.pwmWrite(1)
        time.sleep(1)

except KeyboardInterrupt:
    print('Encerrando...')
    led.release()