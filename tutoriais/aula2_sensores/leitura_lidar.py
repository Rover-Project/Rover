"""
Aula 2 - Lendo o Lidar TF-Luna.

Mostra as três grandezas de cada leitura: distância (cm), força do sinal e
temperatura do chip. No PC o Lidar é simulado: o script muda a distância
simulada para imitar um obstáculo se aproximando.

Executar (na pasta tutoriais/):  python aula2_sensores/leitura_lidar.py
"""
import time
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"

with Rover.from_config(CONFIG) as rover:
    lidar = rover.lidar
    simulado = hasattr(lidar, "set_distance")   # só o Lidar simulado tem set_distance()

    for i in range(10):
        if simulado:
            lidar.set_distance(150 - 15 * i)     # obstáculo se aproximando

        distancia, forca, temperatura = lidar.get_read()
        valida = lidar.get_distance()           # None se a leitura não for confiável
        print(f"bruto: {distancia:4d} cm  força: {forca:5d}  temp: {temperatura:4.1f} °C"
              f"  |  get_distance(): {valida}  obstáculo a 30 cm? {lidar.is_obstacle(30)}")
        time.sleep(0.2)
