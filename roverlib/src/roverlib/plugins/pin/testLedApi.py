from pin import Pin
from pin import PinMode

import time


led = Pin(18, PinMode.DIGITAL_OUT)

try:

    while True:

        print("ON")

        led.on()

        time.sleep(1)

        print("OFF")

        led.off()

        time.sleep(1)

except KeyboardInterrupt:
    print("Encerrando...")
    led.release()