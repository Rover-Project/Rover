"""
Aula 2 - Comportamento reativo com uma máquina de estados.

O Rover avança até encontrar um obstáculo, gira até o caminho ficar livre e
volta a avançar. A transição usa histerese: entra em GIRAR abaixo de
LIMITE_PERTO e só volta a AVANCAR acima de LIMITE_LONGE.

No PC, um "mundo" simples simula o que o Lidar veria: a distância diminui
enquanto o Rover avança e, ao girar, aparece um novo caminho.

Executar (na pasta tutoriais/):  python aula2_sensores/maquina_estados.py
"""
import random
import time
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"

LIMITE_PERTO = 30     # cm: abaixo disso, obstáculo
LIMITE_LONGE = 45     # cm: acima disso, caminho livre (histerese de 15 cm)
VELOCIDADE = 40
PERIODO = 0.05        # s entre decisões (20 Hz)
DURACAO = 15          # s de execução


class MundoSimulado:
    """Distância à frente do Rover, atualizada conforme a ação (apenas no PC)."""

    def __init__(self, seed=3):
        self.rng = random.Random(seed)
        self.distancia = 120.0

    def atualizar(self, estado, dt):
        if estado == "AVANCAR":
            self.distancia -= 25 * dt                  # aproxima ~25 cm/s
        elif estado == "GIRAR":
            # Ao girar, a direção muda: com o tempo aparece um caminho livre
            if self.rng.random() < 2.0 * dt:
                self.distancia = self.rng.uniform(20, 150)
        return max(self.distancia, 5)


def decidir(estado, distancia):
    """Transições da máquina de estados. Retorna o próximo estado."""
    if distancia is None:              # leitura inválida: por segurança, para
        return "PARADO"
    if estado in ("AVANCAR", "PARADO") and distancia < LIMITE_PERTO:
        return "GIRAR"
    if estado in ("GIRAR", "PARADO") and distancia > LIMITE_LONGE:
        return "AVANCAR"
    return estado


def agir(rover, estado):
    if estado == "AVANCAR":
        rover.move.forward(VELOCIDADE)
    elif estado == "GIRAR":
        rover.move.turn_right(VELOCIDADE)
    else:
        rover.move.stop()


with Rover.from_config(CONFIG) as rover:
    simulado = hasattr(rover.lidar, "set_distance")
    if simulado:
        rover.lidar.verbose = False          # o mundo muda a distância a cada passo
    mundo = MundoSimulado()
    estado = "PARADO"
    inicio = time.monotonic()

    while time.monotonic() - inicio < DURACAO:
        if simulado:
            rover.lidar.set_distance(mundo.atualizar(estado, PERIODO))

        distancia = rover.lidar.get_distance()
        novo = decidir(estado, distancia)
        if novo != estado:
            print(f"t={time.monotonic() - inicio:5.1f} s  d={distancia} cm  {estado} -> {novo}")
            estado = novo
            agir(rover, estado)
        time.sleep(PERIODO)
