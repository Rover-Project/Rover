from gpiozero import Servo
from time import sleep
import sys
import termios
import tty

pin180 = 23
pin360 = 24

# Configuração dos Servos
servo_a = Servo(pin180) 
servo_b = Servo(pin360) 

pos_a = 0.0
pos_b = 0.0
passo = 0.1

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

print("Controle Anti-Tremor Ativado!")
print("Movimente e o motor 'relaxará' após 0.3s")

try:
    while True:
        tecla = get_key().lower()
        if tecla == 'q': break

        # Movimentação
        if tecla == 'w': 
            pos_a = min(1.0, pos_a + passo)
        elif tecla == 's': 
            pos_a = max(-1.0, pos_a - passo)
        if tecla == 'i': 
            pos_b = min(1.0, pos_b + passo)
        elif tecla == 'k': 
            pos_b = max(-1.0, pos_b - passo)

        # 1. Envia o sinal para mover
        servo_a.value = pos_a
        servo_b.value = pos_b
        
        print(f"Posição A: {pos_a}")
        print(f"Posição B: {pos_b}")
        
        # 2. Espera o motor chegar na posição (ajuste se o movimento for longo)
        sleep(0.3) 
        
        # 3. "Desliga" o sinal (Cura o tremor)
        servo_a.value = None
        servo_b.value = None

        sys.stdout.write(f"\rA: {pos_a:+.1f} | B: {pos_b:+.1f} [Sinal OFF - Sem Tremor]")
        sys.stdout.flush()

except KeyboardInterrupt:
    pass