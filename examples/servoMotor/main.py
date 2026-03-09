from roverlib.plugins.servoMotor.servo180 import Servo180
from roverlib.plugins.servoMotor.servo360 import Servo360

import time

if __name__ == "__main__":
    pin180 = 23

    servo180 = Servo180(pin180)
    servo180.start()

    servo180.set_angle(0)
    last_angle = 0
    
    try:
        while True:
            angle = int(input("Qual angulo deseja?: "))
            servo180.set_angle(angle)
            time.sleep(1)

    except KeyboardInterrupt:
        servo180.stop()