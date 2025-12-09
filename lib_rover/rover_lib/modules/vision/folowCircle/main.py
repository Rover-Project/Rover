from circleDetect import CircleDetect
from movement.robot import Robot
from utils.config_manager import Config
import time

if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 480 
    THRES = 10  # Delimita um espaço no eixo X para considerar o centro
    SPEED = 50  # Velocidade de rotação
    
    circleDetect = CircleDetect()
    circleDetect.cameraStart(HEIGHT, WIDTH)  # Inicia a câmera
    
    pins_motors = Config.get("gpio")
    robot = Robot(
        left=pins_motors["motor_esquerdo"],
        right=pins_motors["motor_direito"]
    )
    
    x_center = {
        "low": (WIDTH // 2) - THRES,
        "high": (WIDTH // 2) + THRES
    }

    while True:
        circles = circleDetect.getCircle()
        
        if circles is None:
            robot.turn_right(SPEED)  # Rotaciona procurando um círculo
        
        else:
            if len(circles) > 1:
                robot.stop()
            else:
                x, y, r = circles[0]  # Agora circles[0] já contém (x, y, r)
                
                if x > x_center["high"]:
                    robot.turn_right(SPEED)

                elif x < x_center["low"]:
                    robot.turn_left(SPEED)
        
        time.sleep(1)
