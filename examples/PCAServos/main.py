import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Inicializa I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa PCA9685
pca = PCA9685(i2c)
pca.frequency = 50  # 50Hz padrão para servo

# Função para controlar servo contínuo
def set_servo_speed(channel, speed):
    """
    speed: -1.0 (máx reverso) até 1.0 (máx frente)
    0 = parado
    """
    neutral = 375  
    range_val = 100  

    pulse = int(neutral + speed * range_val)
    pca.channels[channel].duty_cycle = pulse

try:
    while True:
        print("Parado")
        set_servo_speed(0, 0)
        set_servo_speed(1, 0)
        time.sleep(2)

        print("Girando pra frente")
        set_servo_speed(0, 0.5)
        set_servo_speed(1, 0.5)
        time.sleep(3)

        print("Girando pra trás")
        set_servo_speed(0, -0.5)
        set_servo_speed(1, -0.5)
        time.sleep(3)

except KeyboardInterrupt:
    print("Encerrando")
    pca.deinit()