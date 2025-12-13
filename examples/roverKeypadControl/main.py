from lib_rover.rover_lib.modules.movement.robot import Robot
from lib_rover.rover_lib.modules.camera.cameraModule import CameraModule
from lib_rover.rover_lib.utils.config_manager import Config
from lib_rover.rover_lib.modules.camera.webcam import Webcam
import cv2 as openCv

if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 640
    
    # Carrega configuração da gpio
    pins_motors = Config.get("gpio")
    letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    # Inicia motores
    robot = Robot(left=letf, right=right)
    speed = 50 # Velocidade inicial
    
    try:
        camera = CameraModule(HEIGHT, WIDTH)
    except:
        camera = Webcam(HEIGHT, WIDTH)
    
    while True:
        frame = camera.get_frame()
        
        speed = max(0, min(speed, 100))        
        
        openCv.imshow("Rover", frame)
        
        key = openCv.waitKey(1) & 0xFF # Espera resposta do teclado
        
        if key == ord("w"):
            robot.forward(speed)
            pass
        
        elif key == ord("a"):
            robot.turn_left(speed)
            pass
        
        elif key == ord("d"):
            robot.turn_right(speed)
            pass
        
        elif key == ord("s"):
            robot.backward(speed)
            pass
            
        elif key == ord("e"):
            speed = max(0, min(speed + 10, 100))
        
        elif key == ord("r"):
            speed = max(0, min(speed - 10, 100))
        
        elif key == ord("q"):
            break
    
        else:
            pass
            robot.stop()
        
        print(speed)
    
    robot.cleanup()
    camera.cleanup()
    openCv.destroyAllWindows()
        