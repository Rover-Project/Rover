from ..modules.movement.robot import Robot

class Motor:
    """
    Classe para controlar os motores usando gpiozero.Robot.
    """
    def __init__(self, left_pins, right_pins, initial_speed=0.5):
        """
        Inicializa o motor com os pinos e a velocidade inicial.
        """
        # Criacao do motor.
        self.motor = Robot(left=left_pins, right=right_pins)
        self._speed = initial_speed # Velocidade inicial

    @property
    def speed(self):
        """ Getter para a velocidade. """
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        """ Setter para a velocidade, garante que esteja entre 0.0 e 1.0. """
        self._speed = max(0.0, min(1.0, new_speed))

    def forward(self):
        """ Move para frente com a velocidade atual. """
        self.motor.forward(self._speed) # type: ignore

    def backward(self):
        """ Move para trás com a velocidade atual. """
        self.motor.backward(self._speed) # type: ignore

    def left(self):
        """ Move para a esquerda (gira no lugar ou curva) com a velocidade atual. """
        self.motor.left(self._speed) # type: ignore

    def right(self):
        """ Move para a direita (gira no lugar ou curva) com a velocidade atual. """
        self.motor.right(self._speed) # type: ignore

    def stop(self):
        """ Para o motor. """
        self.motor.stop()