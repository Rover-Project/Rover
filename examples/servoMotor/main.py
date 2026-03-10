from roverlib.plugins.servoMotor.servo180 import Servo180
from roverlib.utils.config_manager import Config
from pathlib import Path
from roverlib.plugins.servoMotor.servo360 import Servo360

import time

if __name__ == "__main__":
    
    config = Config(
        Path(__file__).parent / "config.yaml"
    )
    
    config_motor = config.get("motor")
    
    pin180 = config_motor["servo180"]
    pin360 = config_motor["servo360"]
    
    servo180 = Servo180(pin180)
    servo180.start()
    
    servo360 = Servo360(pin360)
    servo360.start()

    servo180.set_angle(0)
    last_angle = 0
    
    try:
        while True:
            servo_index = int(input("Qual servo: "))
            
            if servo_index == 0: 
                angle = int(input("Ângulo: "))
                servo180.set_angle(angle)
                time.sleep(1)
                
            elif servo_index == 1:
                time_rot = float(input("Tempo de rotação: "))
                
                time_rot = min(time_rot, 0.5)
                servo360.mover_h(0.5)
                time.sleep(time_rot)
                servo360.stop()
                
            else:
                print("Valor invalido")
                
                
    except KeyboardInterrupt:
        servo180.stop()