import time
from pin import Pin, PinMode

# Inicializa o GPIO 18 (Pino físico 12)
led = Pin(18, PinMode.PWM)

try:
    print("Iniciando ciclo de brilho...")
    while True:
        for brilho in [0.1, 0.5, 0.9]:
            print(f"Brilho: {brilho*100}%")
            led.pwm(brilho)
            time.sleep(2)

except KeyboardInterrupt:
    print('\nEncerrando e liberando hardware...')
    led.release()