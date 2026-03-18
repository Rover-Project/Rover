from gpiozero import PWMLED
from time import sleep

# Exemplo: LED no pino GPIO 12 (Pino 32 físico)
led = PWMLED(12)

while True:
    led.value = 0.5  # Define 50% de brilho (Duty Cycle)
    sleep(1)
    led.value = 1.0  # 100% de brilho
    sleep(1)
