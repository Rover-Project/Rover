import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)

# Cria PWM em 50Hz (servo padrão)
pwm = GPIO.PWM(15, 100)
pwm.start(0)

def set_angle(angle):
    # Converte ângulo (0–180) em duty cycle
    duty = 2 + (angle / 18)
    GPIO.output(15, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(15, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        for angle in [0, 45, 90, 100, 120]:
            print(f"Movendo para {angle} graus")
            set_angle(angle)
            time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()