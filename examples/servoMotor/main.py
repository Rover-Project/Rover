from roverlib.plugins.servoMotor.servo180 import Servo180
from roverlib.plugins.servoMotor.servo360 import Servo360

import time

if __name__ == "__main__":
    pin180 = 23
    pin360 = 24

    servo180 = Servo180(pin180)
    servo180.start()
    
    servo360 = Servo360(pin360)
    servo360.start()

    servo180.set_angle(0)
    servo180.set_angle(0)
    last_angle = 0
    
    try:
        while True:
            angle = int(input("Qual angulo deseja?: "))
            servo180.set_smooth_angle(last_angle, angle)
            time.sleep(1)
            servo360.set_smooth_speed(last_angle, angle)
            time.sleep(1)

    except KeyboardInterrupt:
        servo180.stop()
        servo360.stop()