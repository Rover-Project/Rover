"""
Aula 1 - Polígono regular em malha aberta.

Percorre um polígono de N lados usando turn_degrees(). O ângulo de cada giro
é estimado por tempo: TEMPO_360 é quanto o Rover leva para dar uma volta
completa na velocidade de giro, e precisa ser medido no robô.

Executar (na pasta tutoriais/):  python aula1_locomocao/poligono.py
"""
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"

LADOS = 5             # número de lados do polígono
TEMPO_LADO = 1.5      # segundos andando em cada lado
VELOCIDADE = 50
TEMPO_360 = 12.0      # segundos para girar 360° com velocidade 55 (meça no seu Rover!)

angulo_externo = 360 / LADOS

with Rover.from_config(CONFIG) as rover:
    for lado in range(LADOS):
        print(f"Lado {lado + 1}/{LADOS}")
        rover.move.forward(VELOCIDADE, duration=TEMPO_LADO)
        rover.move.turn_degrees(angulo_externo, time_to_turn=TEMPO_360)
