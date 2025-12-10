from modules.movement.robot import Robot
from utils.config_manager import Config
import time
from circleDetect import *
import cv2 as openCv

def turn_righ(robot: Robot, speed=100.0):
    robot.move(speed_left=(speed * 0.6), speed_right=0)

def turn_left(robot: Robot, speed=100.0):
    robot.move(speed_left=(-speed * 0.6), speed_right=speed)

def forward(robot: Robot, speed=100.0):
    robot.move(speed_left=speed * 0.7, speed_right=speed)

def backward(robot: Robot, speed=100.0):
    robot.move(speed_left=(-speed * 0.7), speed_right=-speed)
    
    
if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 480
    THRES = 30  # Delimita um espaço no eixo X para considerar o centro
    SPEED = 100  # Velocidade de rotação

    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (640, 640)})
    picam.configure(config)
    picam.start()

    circleHistory = None  # média acumulada
    cont = 0
    LIMIAR = 40  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 10  # número máximo de frames sem detecção
    noDetCounter = 0

    pins_motors = Config.get("gpio")
    letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    robot = Robot(left=letf, right=right)

    x_center = {
        "low": (HEIGHT // 2),
        "high": (HEIGHT // 2)
    }

    CENTER_LIMIAR = 100
    BUFFER_SIZE = 5  # quantidade de últimas detecções
    last_circle = None  # cria o buffer circular
    RED_THRESHOLD = 200000

    while True:
        frame = picam.capture_array()
        mask, _, _ = colorDualSegmentation(frame)
        hough, _ = houghDetect(mask)
        contorno = circleCannyDetect(mask)

        # escolhe a melhor detecção entre hough e contorno
        if hough is not None and contorno is not None:
            det = circleVoting(hough, contorno)
        elif hough is not None:
            det = hough
        elif contorno is not None:
            det = contorno
        else:
            det = None

        if det is not None:
            noDetCounter = 0  # reset contador de frames sem detecção

            if circleHistory is None or not inInterval(det, circleHistory, LIMIAR):
                circleHistory = list(det)
                cont = 1
            else:
                circleHistory[0] += det[0]
                circleHistory[1] += det[1]
                circleHistory[2] += det[2]
                last_circle = circleHistory # captura o ultimo ciculo
                cont += 1

        else:
            noDetCounter += 1
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None
                cont = 0

        txt = "Nenhum circulo detectado"
        if circleHistory and cont > 0:
            x = circleHistory[0] // cont
            y = circleHistory[1] // cont
            r = circleHistory[2] // cont
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
            txt = f"X={x}  Y={y}  R={r}"

        openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        openCv.imshow("Deteccao Final", frame)
        openCv.imshow("Mascara", mask)

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

        red_area = openCv.countNonZero(mask)

        if circleHistory is None:
            print(f"Area vermelha: {red_area}")
            if red_area >= RED_THRESHOLD: # Chegou perto o suficiente da bola
                robot.stop()
            elif last_circle:
                last_x, last_y, last_r = last_circle
                if last_x > WIDTH // 2:
                    robot.move(60, -60)  # gira para direita
                else:
                    robot.move(-60, 60)  # gira para esquerda
            else:
                print("Nenhum circulo foi detectado")
                robot.move(-60, 60)  # rotaciona procurando um círculo

        else:
            x, y, r = circleHistory
            if x > x_center["high"] + CENTER_LIMIAR:
                robot.move(60, -60)
            elif x < x_center["low"] - CENTER_LIMIAR:
                robot.move(-60, 60)
            else:
                robot.move(70, 100)

        time.sleep(0.1)

    picam.stop()
    openCv.destroyAllWindows()
