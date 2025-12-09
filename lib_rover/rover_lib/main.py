from modules.movement.robot import Robot
from utils.config_manager import Config
import time
from circleDetect import CircleDetect
import cv2 as openCv
import numpy

def turn_righ(robot: Robot, speed=100.0):
    robot.move(speed * 0.6, -speed)
    
def turn_left(robot: Robot, speed=100.0):
    robot.move(-speed * 0.5, speed)

if __name__ == "__main__":
    
    pins_motors = Config.get("gpio")

    letf = (int(pins_motors["motor_esquerdo"]["in1"]), int(pins_motors["motor_esquerdo"]["in2"]))
    right = (int(pins_motors["motor_direito"]["in3"]), int(pins_motors["motor_direito"]["in4"]))

    robot = Robot(
        left=letf,
        right=right
    )
    
    image = numpy.array([480 * numpy.zeros(480)])
    
    while True:
        openCv.imshow("Controler", image)
        
        key = openCv.waitKey(0) & 0xFF
        
        if key == ord("a"):
            turn_left(robot)
        elif key == ord("d"):
            turn_righ(robot)
        elif key == ord("q"):
            
            break
    
    openCv.destroyAllWindows()
        
        
        
    
    
    
    # HEIGHT = 640
    # WIDTH = 480
    # THRES = 30  # Delimita um espaço no eixo X para considerar o centro
    # SPEED = 100  # Velocidade de rotação

    # circleDetect = CircleDetect()
    # circleDetect.cameraStart(HEIGHT, WIDTH)  # Inicia a câmera

    # pins_motors = Config.get("gpio")

    # letf = (int(pins_motors["motor_esquerdo"]["in1"]), int(pins_motors["motor_esquerdo"]["in2"]))
    # right = (int(pins_motors["motor_direito"]["in3"]), int(pins_motors["motor_direito"]["in4"]))

    # robot = Robot(
    #     left=letf,
    #     right=right
    # )

    # x_center = {
    #     "low": (HEIGHT // 2) - THRES,
    #     "high": (HEIGHT // 2) + THRES
    # }

    # while True:
    #     circles, mask, frame = circleDetect.getCircle()
        
    #     # Desenhar círculos detectados
    #     if circles is not None:
    #         circles = numpy.uint16(numpy.around(circles))

    #         for (x, y, r) in circles[0, :]:
    #             openCv.circle(frame, (x, y), r, (0, 255, 0), 2)  # círculo
    #             openCv.circle(frame, (x, y), 2, (0, 0, 255), 3)  # centro
    #             openCv.putText(
    #                 frame, 
    #                 f"({x},{y}) r={r}", 
    #                 (x - 40, y - r - 10),
    #                 openCv.FONT_HERSHEY_SIMPLEX, 
    #                 0.5, 
    #                 (255, 255, 255), 
    #                 2
    #             )

    #     # Mostrar imagens
    #     openCv.imshow("Deteccao da Cor Capturada", frame)
    #     openCv.imshow("Mascara Atual", mask)

    #     if openCv.waitKey(1) & 0xFF == ord('q'):
    #         break

    #     if circles is None:
    #         print("Nenhum circulo foi detectado")
    #         robot.move(-SPEED * 0.5, SPEED)  # Rotaciona procurando um círculo

    #     else:
    #         if len(circles[0]) > 1:
    #             print("Multiplos circulos detectados")
    #             robot.stop()
    #         else:
    #             x, y, r = circles[0][0]  # Agora circles[0] já contém (x, y, r)

    #             print(f"Circulo unico detectado: centro - ({x}, {y}); raio - {r}")
    #             print(f"Tentando achar o centro: ({x_center['low']},{x_center['high']})")

    #             if x > x_center["high"]:
    #                 robot.move(SPEED * 40, -SPEED)

    #             elif x < x_center["low"]:
    #                 robot.move(-SPEED * 40, SPEED)
    #             else:
    #                 robot.stop()

    #     time.sleep(0.5)