"""
Exemplo 1 - Movimento: o Rover percorre um quadrado.

Execute na pasta do projeto:   python -m src.examples.quadrado

Ajuste TEMPO_GIRO até o Rover girar cerca de 90°.
"""
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[2] / "config.yaml"

VELOCIDADE = 50
TEMPO_LADO = 1.5   # segundos andando em cada lado
TEMPO_GIRO = 0.6   # segundos girando (≈ 90°)


def main():
    with Rover.from_config(CONFIG) as rover:
        for lado in range(4):
            print(f"Lado {lado + 1}")
            rover.move.forward(VELOCIDADE, duration=TEMPO_LADO)
            rover.move.turn_right(VELOCIDADE, duration=TEMPO_GIRO)


if __name__ == "__main__":
    main()
