"""
Aula 1 - Modelo cinemático do robô diferencial.

Simula a trajetória (x, y, theta) produzida por uma sequência de comandos
move(velocidade_direita, velocidade_esquerda, duração), integrando o modelo:

    v     = (vR + vL) / 2          velocidade linear
    omega = (vR - vL) / L          velocidade angular
    x'    = v cos(theta),  y' = v sin(theta),  theta' = omega

Executar (na pasta tutoriais/):  python aula1_locomocao/cinematica.py
A figura é salva em aula1_locomocao/saida/trajetorias.png.

Os parâmetros físicos abaixo são estimativas: meça-os no seu Rover (veja a aula).
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # salva figuras em arquivo, sem precisar de janela
import matplotlib.pyplot as plt

# ---------------- parâmetros do Rover (estimativas: meça no robô) ----------------
VEL_MAX = 0.30      # m/s de uma roda com velocidade 100
BITOLA = 0.20       # L: distância entre as rodas, em metros
DT = 0.01           # passo de integração, em segundos

SAIDA = Path(__file__).resolve().parent / "saida"


def roda(velocidade):
    """Converte a velocidade da RoverLib (-100 a 100) em m/s, supondo relação linear."""
    return VEL_MAX * velocidade / 100.0


def simular(comandos, pose=(0.0, 0.0, 0.0), fator_direita=1.0, fator_esquerda=1.0):
    """
    Integra a cinemática para uma lista de comandos (vel_direita, vel_esquerda, duração).

    fator_direita/fator_esquerda simulam motores diferentes (ex.: 0.95 = 5% mais lento).
    Retorna as listas de x e y e a pose final (x, y, theta).
    """
    x, y, theta = pose
    xs, ys = [x], [y]
    for vel_d, vel_e, duracao in comandos:
        v_r = roda(vel_d) * fator_direita
        v_l = roda(vel_e) * fator_esquerda
        v = (v_r + v_l) / 2
        omega = (v_r - v_l) / BITOLA
        for _ in range(int(round(duracao / DT))):
            x += v * math.cos(theta) * DT
            y += v * math.sin(theta) * DT
            theta += omega * DT
            xs.append(x)
            ys.append(y)
    return xs, ys, (x, y, theta)


def tempo_para_girar(graus, velocidade=50):
    """Tempo de giro no próprio eixo (rodas opostas) para virar `graus`, pelo modelo."""
    omega = 2 * roda(velocidade) / BITOLA      # rad/s
    return math.radians(abs(graus)) / omega


def quadrado(lado_s=2.0, velocidade=50):
    """Comandos para um quadrado: anda `lado_s` segundos e gira 90° à esquerda, 4 vezes."""
    giro = tempo_para_girar(90, velocidade)
    passo = [(velocidade, velocidade, lado_s), (velocidade, -velocidade, giro)]
    return passo * 4


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    print(f"Giro de 90° a velocidade 50 leva {tempo_para_girar(90):.2f} s pelo modelo.")

    casos = {
        "quadrado ideal": dict(comandos=quadrado()),
        "quadrado, motor direito 5% mais lento": dict(comandos=quadrado(), fator_direita=0.95),
        "círculo (direita 60, esquerda 40)": dict(comandos=[(60, 40, 6.0)]),
    }

    plt.figure(figsize=(7, 7))
    for nome, caso in casos.items():
        xs, ys, (x, y, theta) = simular(**caso)
        plt.plot(xs, ys, label=nome)
        print(f"{nome:40s} pose final: x={x:+.2f} m  y={y:+.2f} m  theta={math.degrees(theta):+.0f}°")

    plt.axis("equal")
    plt.grid(True)
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.title("Trajetórias previstas pelo modelo cinemático")
    plt.legend()
    arquivo = SAIDA / "trajetorias.png"
    plt.savefig(arquivo, dpi=120)
    print(f"Figura salva em {arquivo}")
