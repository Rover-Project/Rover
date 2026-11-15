"""
Aula 1 - Primeiros comandos de movimento.

Executar (na pasta tutoriais/):  python aula1_locomocao/primeiros_comandos.py
No PC, os motores são simulados e cada comando aparece no terminal.
"""
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"

with Rover.from_config(CONFIG) as rover:
    print(rover)

    # Velocidades de 0 a 100 (porcentagem do PWM); duration em segundos
    rover.move.forward(speed=50, duration=1)
    rover.move.turn_right(speed=50, duration=0.5)

    # move(): velocidade de cada lado. Lados diferentes -> curva.
    rover.move.move(speed_right=60, speed_left=30, duration=1)   # curva para a esquerda
    rover.move.move(speed_right=-40, speed_left=40, duration=1)  # giro no próprio eixo, para a direita

    rover.move.backward(speed=40, duration=1)
