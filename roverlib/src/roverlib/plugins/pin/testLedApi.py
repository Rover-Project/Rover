from pin import Pin, PinMode
import time

led = Pin(15, PinMode.OUTPUT)

try:
    for i in range(10):
        print("ON")
        led.write(1)
        time.sleep(1)

        print("OFF")
        led.write(0)
        time.sleep(1)

finally:
    print("Encerrando...")
