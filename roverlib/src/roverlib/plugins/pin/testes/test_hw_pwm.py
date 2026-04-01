import _path  # noqa
import time
from pin import Pin, PinMode

FREQ = 1000

with Pin(18, PinMode.PWM) as led:
    print(f"Pino: {led.number}  Modo: {led.mode}  Freq: {FREQ} Hz")

    print("[1] Fade in")
    for d in [i/20 for i in range(21)]:
        led.pwm(d, FREQ)
        time.sleep(0.06)

    time.sleep(0.5)

    print("[2] Fade out")
    for d in [i/20 for i in range(20, -1, -1)]:
        led.pwm(d, FREQ)
        time.sleep(0.06)

    print(f"Duty atual: {led.duty:.2f}  Freq atual: {led.frequency} Hz")
    led.stop_pwm()
    print("OK")