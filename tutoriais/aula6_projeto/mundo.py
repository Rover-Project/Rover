"""
Aula 6 - Mundo simulado para o projeto integrador.

Simula um Rover numa sala com uma bola vermelha: guarda a posição e a direção do
robô, atualiza-as a partir das velocidades das rodas (modelo da aula 1), gera o
frame que a câmera veria (cena sintética da aula 3) e a distância que o Lidar
mediria à frente.

Assim, o projeto inteiro roda no PC, sem câmera nem robô.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cena import gerar_cena, Objeto, VERMELHO  # noqa: E402

LARGURA, ALTURA = 640, 480
FOV = math.radians(62)
FOCAL = (LARGURA / 2) / math.tan(FOV / 2)
RAIO_BOLA = 0.035          # m (bola de 7 cm)
VEL_MAX = 0.30             # m/s de uma roda a 100
BITOLA = 0.20              # m
PAREDE = 2.5               # m: o Lidar mede até a parede quando não vê a bola


class MundoSimulado:
    def __init__(self, bola=(1.5, 0.8)):
        self.x, self.y, self.theta = 0.0, 0.0, 0.0
        self.bola = bola
        self.vel_d = self.vel_e = 0.0

    def comandar(self, vel_direita, vel_esquerda):
        """Registra o último comando enviado às rodas (-100 a 100)."""
        self.vel_d, self.vel_e = vel_direita, vel_esquerda

    def atualizar(self, dt):
        v_r = VEL_MAX * self.vel_d / 100
        v_l = VEL_MAX * self.vel_e / 100
        v, omega = (v_r + v_l) / 2, (v_r - v_l) / BITOLA
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        self.theta += omega * dt

    def _bola_relativa(self):
        dx, dy = self.bola[0] - self.x, self.bola[1] - self.y
        distancia = math.hypot(dx, dy)
        angulo = math.atan2(dy, dx) - self.theta
        angulo = (angulo + math.pi) % (2 * math.pi) - math.pi     # entre -pi e pi
        return distancia, angulo

    def frame(self, seed=0):
        """Imagem BGR que a câmera veria agora."""
        distancia, angulo = self._bola_relativa()
        objetos = []
        if abs(angulo) < FOV / 2 and distancia > 0.05:
            # ângulo positivo = bola à esquerda (anti-horário) -> aparece à esquerda da imagem
            x = LARGURA / 2 - FOCAL * math.tan(angulo)
            raio = max(3, FOCAL * RAIO_BOLA / distancia)
            objetos.append(Objeto("circulo", (int(x), ALTURA // 2), int(raio), VERMELHO))
        img, _ = gerar_cena(LARGURA, ALTURA, objetos=objetos, seed=seed)
        return img

    def distancia_lidar_cm(self):
        """Distância à frente: a bola, se estiver bem à frente; senão, a parede."""
        distancia, angulo = self._bola_relativa()
        if abs(angulo) < math.radians(2):
            return 100 * max(distancia - RAIO_BOLA, 0.05)
        return 100 * PAREDE

    def __repr__(self):
        d, a = self._bola_relativa()
        return f"Rover em ({self.x:.2f}, {self.y:.2f}) m, bola a {d:.2f} m e {math.degrees(a):+.0f}°"
