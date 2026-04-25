import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Inicialização I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa PCA9685
pca = PCA9685(i2c)
pca.frequency = 50  # 50Hz para servo

# Converte velocidade em duty_cycle 
def set_servo_speed(channel, speed):
    # Ajuste fino 
    min_pulse = 2000
    max_pulse = 8000
    neutral = 5000

    pulse = int(neutral + speed * (max_pulse - min_pulse) / 2)

    # Garante que não ultrapasse limites
    pulse = max(min_pulse, min(max_pulse, pulse))

    pca.channels[channel].duty_cycle = pulse

def parar(ch):
    set_servo_speed(ch, 0)

def frente(ch):
    set_servo_speed(ch, 0.5)

def tras(ch):
    set_servo_speed(ch, -0.5)

def parar_todos():
    for i in range(16):
        set_servo_speed(i, 0)

try:
    while True:
        ch = int(input("Canal do servo (0-15): "))
        cmd = input("Digite comando (f=frente / t=tras / p=parar / s=sair): ").lower()

        if cmd == "f":
            frente(ch)
            time.sleep(0.5)
            parar(ch)

        elif cmd == "t":
            tras(ch)
            time.sleep(0.5)
            parar(ch)

        elif cmd == "p":
            parar(ch)

        elif cmd == "s":
            break

        else:
            print("Comando inválido")

except KeyboardInterrupt:
    print("Encerrando")

finally:
    parar_todos()
    pca.deinit()