from gpiozero import Servo
from time import sleep
import sys
import termios
import tty

# Inicialização direta (O gpiozero usa o driver padrão do SO)
# Se o servo estiver 'trepidando', tente usar a propriedade 'frame_width'
servo_a = Servo(15)
servo_b = Servo(14)

pos_a = 0.0
pos_b = 0.0
passo = 0.1 

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

print("Controle Iniciado (Sem PiGPIOFactory)!")
print("Use 'w/s' para Servo A | 'i/k' para Servo B | 'q' para sair")

try:
    while True:
        char = getch()
        if char == 'q':
            break

        # Lógica de incremento
        if char == 'w': pos_a = min(1.0, pos_a + passo)
        elif char == 's': pos_a = max(-1.0, pos_a - passo)
        elif char == 'i': pos_b = min(0.4, pos_b + passo)
        elif char == 'k': pos_b = max(-0.4, pos_b - passo)

        # Aplica valor
        servo_a.value = pos_a
        servo_b.value = pos_b
        
        print(f"\rA: {pos_a:.1f} | B: {pos_b:.1f}", end="")

except KeyboardInterrupt:
    pass

print("\nEncerrando...")