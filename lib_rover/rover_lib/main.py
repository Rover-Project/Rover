from modules.movement.robot import Robot
from utils.config_manager import Config
import time
from circleDetect import *
import cv2 as cv
from picamera2 import Picamera2

def turn_right(robot: Robot, speed=50.0):
    robot.move(speed_left=speed, speed_right=-speed)

def turn_left(robot: Robot, speed=50.0):
    robot.move(speed_left=-speed, speed_right=speed)

def stop(robot: Robot):
    robot.stop()

if __name__ == "__main__":
    WIDTH = 640
    HEIGHT = 480
    THRES = 30  # tolerância para considerar centralizado
    SPEED = 50  # velocidade do movimento

    picam = Picamera2()
    config = picam.create_preview_configuration(main={"format": "RGB888", "size": (WIDTH, HEIGHT)})
    picam.configure(config)
    picam.start()

    pins_motors = Config.get("gpio")
    left_pins = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right_pins = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    robot = Robot(left=left_pins, right=right_pins)

    x_center_range = {
        "low": (WIDTH // 2) - THRES,
        "high": (WIDTH // 2) + THRES
    }

    try:
        while True:
            frame = picam.capture_array()

            mask, _, _ = colorDualSegmentation(frame)
            hough, _ = houghDetect(mask)
            contorno = circleCannyDetect(mask)

            # escolhe a melhor detecção
            if hough is not None and contorno is not None:
                det = circleVoting(hough, contorno)
            elif hough is not None:
                det = hough
            elif contorno is not None:
                det = contorno
            else:
                det = None

            txt = "Nenhum círculo detectado"
            if det:
                x, y, r = det
                cv.circle(frame, (x, y), r, (0, 255, 0), 3)
                cv.circle(frame, (x, y), 3, (0, 255, 255), -1)
                txt = f"X={x}  Y={y}  R={r}"

                # centraliza o robô
                if x > x_center_range["high"]:
                    turn_right(robot, SPEED)
                elif x < x_center_range["low"]:
                    turn_left(robot, SPEED)
                else:
                    stop(robot)
            else:
                stop(robot)

            cv.putText(frame, txt, (10, 35), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv.imshow("Deteccao Final", frame)
            cv.imshow("Mascara", mask)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.05)  # loop mais responsivo

    except KeyboardInterrupt:
        print("Programa interrompido pelo usuário")
    finally:
        picam.stop()
        cv.destroyAllWindows()
        stop(robot)
