from roverlib.modules.movement.robot import Robot
from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from pathlib import Path
import cv2 as openCv


def set_move(command: str = None, speed: float=50):        
    
    if command == ord("w"):
        robot.forward(speed)
        
    elif command == ord("a"):
        robot.turn_left(speed)
        
    elif command == ord("d"):
        robot.turn_right(speed)
        
    elif command == ord("s"):
        robot.backward(speed)
        
    elif command == ord("e"):
        speed = max(0, min(speed + 10, 100))
    
    elif command == ord("r"):
        speed = max(0, min(speed - 10, 100))
    
    else:
        robot.stop()

    print(speed)
    return speed
    
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
        camera = AfCamera(HEIGHT, WIDTH)
        camera.start()

    except:
        raise RuntimeError("Erro ao abrir câmera")
    
    while True:
        frame = camera.get_frame()
    
        key = openCv.waitKey(100) & 0xFF # Espera resposta do teclado
        speed = set_move(command=key, speed=speed)
        
        if frame is not None:    
            openCv.imshow("Rover", frame)
        
        if key == ord("q"):
            break
        
    robot.cleanup()
    camera.cleanup()
    openCv.destroyAllWindows()