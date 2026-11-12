"""
Exemplo 3 - Sensor: anda para frente e para ao encontrar um obstáculo.

Antes: ative a seção "lidar:" no config.yaml (requer o Lidar TF-Luna conectado).
Execute na pasta do projeto:   python -m src.examples.parar_no_obstaculo
Pressione Ctrl+C para encerrar.
"""
import time
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[2] / "config.yaml"

DISTANCIA_LIMITE = 30  # cm
VELOCIDADE = 40


def main():
    with Rover.from_config(CONFIG) as rover:
        try:
            while True:
                distancia = rover.lidar.get_distance()

                if distancia is None:
                    # Sem leitura confiável: por segurança, fica parado
                    rover.move.stop()
                elif rover.lidar.is_obstacle(DISTANCIA_LIMITE):
                    rover.move.stop()
                    print(f"Obstáculo a {distancia} cm. Parado.")
                else:
                    rover.move.forward(VELOCIDADE)

                time.sleep(0.05)
        except KeyboardInterrupt:
            print("Encerrando...")


if __name__ == "__main__":
    main()
