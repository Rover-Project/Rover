import _path  # noqa
import time
from pin import Pin, PinMode

FREQ = 200

with Pin(2, PinMode.DIGITAL_OUT) as led:
    print("[1] Fade in  (0% → 100%)")
    for d in [i/20 for i in range(21)]:
        led.pwm(d, FREQ)
        print(f"  duty={d:.2f}", end="\r")
        time.sleep(0.08)

    time.sleep(0.5)

    print("\n[2] Fade out (100% → 0%)")
    for d in [i/20 for i in range(20, -1, -1)]:
        led.pwm(d, FREQ)
        print(f"  duty={d:.2f}", end="\r")
        time.sleep(0.08)

    led.stop_pwm()
    print("\nOK")