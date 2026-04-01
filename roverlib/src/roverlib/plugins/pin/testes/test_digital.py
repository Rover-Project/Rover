# test_digital.py
# LED no GPIO 17  (pino físico 11)
# Anodo (+) → resistor 220Ω → GPIO17
# Catodo (−) → GND (pino físico 9)

import time
from pin.pin import Pin, PinMode

with Pin(17, PinMode.DIGITAL_OUT) as led:
    print("[1] LED ON por 2 s")
    led.on()
    time.sleep(2)

    print("[2] LED OFF por 1 s")
    led.off()
    time.sleep(1)

    print("[3] Blink 10x")
    for i in range(10):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

    print("OK — release() automático ao sair do with")
