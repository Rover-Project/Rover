from .bin import pin as native

PinMode = native.PinMode


class Pin:

    def __init__(self, number, mode):
        self._pin = native.Pin(number, mode)

    def on(self):
        self._pin.write(1)

    def off(self):
        self._pin.write(0)

    def read(self):
        return self._pin.read()

    def pwm(self, duty):
        self._pin.pwmWrite(duty)

    def release(self):
        self._pin.release()
