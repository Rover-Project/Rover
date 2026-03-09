"""
    Driver para controle de motores via GPIO usando uma ponte-H L298N e PWM.
    Responsável pela comunicação direta com o hardware da Raspberry Pi.
"""
import time

# Verifica se está na raspbarry 
try:
    import RPi.GPIO as GPIO # type: ignore
    GPIO_AVAILABLE = True
    
except (RuntimeError, ModuleNotFoundError):
    GPIO_AVAILABLE = False
    print("AVISO: RPi.GPIO não detectado. Este módulo requer Raspberry Pi com RPi.GPIO instalado.")

class Servo180:

    def __init__(self, pin, frenquency=50):
        self.pin = pin
        self.frenquency = frenquency

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        
    def start(self):
        self.pwm = GPIO.PWM(self.pin, self.frenquency)  # 50Hz
        self.pwm.start(0)

    def set_angle(self, angle):

        duty = 2.5 + (angle / 180) * 10

        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty)

        time.sleep(0.3)

        GPIO.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)

    def set_smooth_angle(self, init, end, step=1, time_step=0.01):
        
        angles = init > end if range(init, end, -step) else range(init, end, step)
        
        for angle in angles:
            self.set_angle(angle)
            time.sleep(time_step)

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()