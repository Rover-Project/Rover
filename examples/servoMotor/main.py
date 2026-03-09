from roverlib.plugins.servoMotor.servo import Servo
import time

if __name__ == "__main__":
    pin180 = 23
    pin360 = 24

    servo180 = Servo(pin180)
    servo180.start()
    
    servo360 = Servo(pin360)
    servo360.start()

    servo180.set_angle(0)
    servo180.set_angle(0)
    last_angle = 0
    
    try:
        while True:
            angle = float(input("Qual angulo deseja?: "))
            servo180.set_smooth_angle(last_angle, angle)
            time.sleep(1)
            servo360.set_smooth_angle(last_angle, angle)
            time.sleep(1)

    except KeyboardInterrupt:
        servo180.stop()
        servo360.stop()