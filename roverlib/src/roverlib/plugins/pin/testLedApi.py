from pin import GPIOPin
from pin import PinMode

import time


led = GPIOPin(15, PinMode.OUTPUT)

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
