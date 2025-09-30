import pygame
from gpiozero import Robot
import sys

# Definição dos pinos
l1 = 11
l2 = 12
r1 = 15
r2 = 16
motor = Robot(left=(l1, l2), right=(r1, r2))
velocidade = 0.6

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((300, 200)) # Cria uma pequena janela
pygame.display.set_caption("Controle do Rover")

print("Controle via janela Pygame (focada):")
print("Setas = Mover | Espaço = Parar | Q = Sair")

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                motor.stop()
                pygame.quit()
                sys.exit()

            # Evento de tecla pressionada
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("Frente")
                    motor.forward(velocidade)
                elif event.key == pygame.K_DOWN:
                    print("Ré")
                    motor.backward(velocidade)
                elif event.key == pygame.K_LEFT:
                    print("Esquerda")
                    motor.left(velocidade)
                elif event.key == pygame.K_RIGHT:
                    print("Direita")
                    motor.right(velocidade)
                elif event.key == pygame.K_SPACE:
                    print("Parado")
                    motor.stop()
                elif event.key == pygame.K_q:
                    motor.stop()
                    pygame.quit()
                    sys.exit()

            # Evento de tecla solta (para o robô)
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    motor.stop()

except KeyboardInterrupt:
    motor.stop()
    pygame.quit()
    sys.exit()