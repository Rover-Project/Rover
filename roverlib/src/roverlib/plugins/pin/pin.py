from .bin.pin import Pin, PinMode


class GPIOPin:

    def __init__(self, pin, mode):

        self.pin = Pin(pin, mode)

    def on(self):

        self.pin.write(1)

    def off(self):

        self.pin.write(0)

    def read(self):

        return self.pin.read()
