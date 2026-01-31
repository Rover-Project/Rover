import click
import time

class Robot:

    def __init__(self, left_motor, right_motor, calibration=None):
        self.left = left_motor
        self.right = right_motor
        self.cal = calibration

        self.left.start()
        self.right.start()

    def forward(self, speed: int, duration: float | None = None):
        self.move(speed, speed)
        if duration:
            time.sleep(duration)
            self.stop()
    
    def move(self, l, r):
        if self.cal:
            l, r = self.cal.apply(l, r)
        self.left.set(l)
        self.right.set(r)

    def stop(self):
        self.left.stop()
        self.right.stop()

    def cleanup(self):
        self.left.cleanup()
        self.right.cleanup()

    def turn_left(self, speed: int, duration: float = 2):
        self.move(-speed, speed)
        time.sleep(duration)
        self.stop()

    def turn_right(self, speed: int, duration: float = 2):
        self.move(speed, -speed)
        time.sleep(duration)
        self.stop()
