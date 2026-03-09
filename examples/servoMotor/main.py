import RPi.GPIO as GPIO
import time

servo180 = 23
servo360 = 24

# Configura o servo 180
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo180, GPIO.OUT)

# Configura o servo 360
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo360, GPIO.OUT)

# Cria PWM em 50Hz para o servo 180
pwm180 = GPIO.PWM(servo180, 50)
pwm180.start(0)

# Cria PWM em 50Hz para o servo 360
pwm360 = GPIO.PWM(servo360, 50)
pwm360.start(0)

def set_angle180(angle):
    # Converte ângulo (0–180) em duty cycle
    duty = 2 + (angle / 18)
    GPIO.output(servo180, True)
    pwm180.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(servo180, False)
    pwm180.ChangeDutyCycle(0)

def set_angle360(angle):
    # Converte ângulo (0–180) em duty cycle
    duty = 2 + (angle / 18)
    GPIO.output(servo360, True)
    pwm360.ChangeDutyCycle(duty * 2)
    time.sleep(0.5)
    GPIO.output(servo360, False)
    pwm360.ChangeDutyCycle(0)

try:
    while True:
        for angle in [0, 45, 90, 100, 120]:
            print(f"Movendo para {angle} graus")
            set_angle180(angle)
            set_angle360(angle)
            time.sleep(5)

except KeyboardInterrupt:
    pwm180.stop()
    pwm360.stop()
    GPIO.cleanup()