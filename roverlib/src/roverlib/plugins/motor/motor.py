"""
    Controle de alto nível dos motores do rover.
    Substitui gpiozero.Robot pelo plugin pin (C++/pybind11).
"""

from .motorDriver import MotorDriver


class Motor:
    """
    Controla os dois motores do rover (esquerdo e direito) via ponte-H L298N.
    Interface idêntica à versão anterior com gpiozero.Robot.
    """

    def __init__(self, left_pins: tuple, right_pins: tuple, initial_speed: int =5, pwm: int = 1000):
        self._left  = MotorDriver(pins=[2,3], pwm_frequency=pwm)        
        self._right = MotorDriver(pins=[1,2], pwm_frequency=pwm)
        self._left.initialize()
        self._right.initialize()
        self._speed = initial_speed

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        self._speed = max(0.0, min(100.0, new_speed))

    def forward(self):
        self._left.set_movement(self._speed,  "FORWARD")
        self._right.set_movement(self._speed, "FORWARD")

    def backward(self):
        self._left.set_movement(self._speed,  "BACKWARD")
        self._right.set_movement(self._speed, "BACKWARD")

    def left(self):
        self._left.set_movement(self._speed,  "BACKWARD")
        self._right.set_movement(self._speed, "FORWARD")

    def right(self):
        self._left.set_movement(self._speed,  "FORWARD")
        self._right.set_movement(self._speed, "BACKWARD")

    def stop(self):
        self._left.stop()
        self._right.stop()

    def cleanup(self):
        self._left.cleanup()
        self._right.cleanup()
