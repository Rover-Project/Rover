"""
Programa principal do seu projeto Rover.

Execute com:   rover run
(no PC os motores são simulados: os comandos aparecem no terminal)
"""
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).parent / "config.yaml"


def main():
    with Rover.from_config(CONFIG) as rover:
        print(rover)

        # Velocidades vão de 0 a 100; duration é o tempo em segundos
        rover.move.forward(speed=50, duration=1)
        rover.move.turn_right(speed=50, duration=0.5)
        rover.move.backward(speed=50, duration=1)

        # Agora é com você! Veja mais ideias em src/examples/.


if __name__ == "__main__":
    main()
