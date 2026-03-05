from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

# Configuração dos Pinos (Substitua pelos pinos que desejar)
# A Raspberry Pi 5 aceita PWM em quase todos os GPIOs via software/kernel
PINO_SERVO_A = 17
PINO_SERVO_B = 27

# Ajuste de correção de pulso (opcional, dependendo do modelo do servo)
# O padrão costuma ser entre 1ms e 2ms
my_factory = PiGPIOFactory()
servo_a = Servo(PINO_SERVO_A, pin_factory=my_factory)
servo_b = Servo(PINO_SERVO_B, pin_factory=my_factory)

try:
    print("Iniciando controle independente...")
    while True:
        # Move Servo A para o mínimo e Servo B para o máximo
        print("A: Min | B: Max")
        servo_a.min()
        servo_b.max()
        sleep(2)

        # Move Servo A para o meio e Servo B para o meio
        print("A: Mid | B: Mid")
        servo_a.mid()
        servo_b.mid()
        sleep(2)

        # Move Servo A para o máximo e Servo B para o mínimo
        print("A: Max | B: Min")
        servo_a.max()
        servo_b.min()
        sleep(2)

        # Exemplo de controle por valor específico (-1 a 1)
        print("Movimento customizado...")
        servo_a.value = 0.5  # Aproximadamente 135 graus
        servo_b.value = -0.5 # Aproximadamente 45 graus
        sleep(2)

except KeyboardInterrupt:
    print("\nPrograma encerrado.")