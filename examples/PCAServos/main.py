import time
import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

def set_servo_speed(channel, speed):
    neutral = 375
    range_val = 100
    pulse = int(neutral + speed * range_val)
    pca.channels[channel].duty_cycle = pulse

def parar(ch):
    set_servo_speed(ch, 0)

def frente(ch):
    set_servo_speed(ch, 0.5)

def tras(ch):
    set_servo_speed(0, -0.5)

try:
    while True:
        ch = int(input("Canal do servo: "))
        cmd = input("Digite comando (f/t/p/q): ").lower()

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
    parar()
    pca.deinit()