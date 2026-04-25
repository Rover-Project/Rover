from roverlib.modules.movement.robot import Robot
from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.utils.config_manager import Config
from pathlib import Path
import cv2 as openCv

if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 640
    
    # Carrega configuração da gpio
    config = Config(Path(__file__).parent / "config.yaml")
    
    pins_motors = config.get("gpio")["motor"]
    letf = pins_motors["left"]
    right = pins_motors["right"]
    
    # Inicia motores
    robot = Robot(left=letf, right=right)
    speed = 50 # Velocidade inicial
    
    try:
        camera = AfCameragt(HEIGHT, WIDTH)
        camera.start()

    except:
        raise RuntimeError("Erro ao abrir câmera")
    
    while True:
        frame = camera.get_frame()
        
        if frame is not None:
        
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