from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
import sys
import termios
import tty

# Configuração de Fábrica para Pi 5
factory = PiGPIOFactory()

# Pinos GPIO (Altere conforme sua montagem)
servo_a = Servo(17, pin_factory=factory)
servo_b = Servo(27, pin_factory=factory)

# Valores Iniciais (0.0 é o meio/90 graus)
pos_a = 0.0
pos_b = 0.0
passo = 0.1 # O quanto o ângulo muda por clique (ajuste a gosto)

def getch():
    """Função para ler teclas do teclado sem precisar dar Enter"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

print("Controle Iniciado!")
print("Servo A: 'w' aumenta, 's' diminui")
print("Servo B: 'i' aumenta, 'k' diminui")
print("Pressione 'q' para sair")

try:
    while True:
        char = getch()
        
        if char == 'q':
            break

        # Lógica Servo A
        if char == 'w':
            pos_a = min(1.0, pos_a + passo) # Limite máximo 1.0
        elif char == 's':
            pos_a = max(-1.0, pos_a - passo) # Limite mínimo -1.0

        # Lógica Servo B
        if char == 'i':
            pos_b = min(1.0, pos_b + passo)
        elif char == 'k':
            pos_b = max(-1.0, pos_b - passo)

        # Aplica os novos valores
        servo_a.value = pos_a
        servo_b.value = pos_b
        
        print(f"\rPosições -> Servo A: {pos_a:.1f} | Servo B: {pos_b:.1f}", end="")

except KeyboardInterrupt:
    pass

print("\nEncerrando...")