from gpiozero import PWMLED
from time import sleep

# Exemplo: LED no pino GPIO 12 (Pino 32 físico)
led = PWMLED(18)

while True:
    led.value = 0.1
    sleep(1)
    led.value = 0.3
    sleep(1)
    led.value = 0.5
    sleep(1)
    led.value = 0.7
    sleep(1)
    led.value = 1.0
    sleep(1)
