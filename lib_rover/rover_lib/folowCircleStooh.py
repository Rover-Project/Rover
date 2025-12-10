from modules.movement.robot import Robot
from utils.config_manager import Config
import time
from circleDetect import *
import cv2 as openCv
from picamera2 import Picamera2

def cameraStart(h=640, w=640, analogic=1.5, exposure = 30000, lighConfig=False):
    picam = Picamera2()
    config = picam.create_preview_configuration(
        main={
            "format": "RGB888", 
            "size": (HEIGHT, WIDTH)
            }
        )
    
    if lighConfig:
        picam.set_controls(
            {
            "AnalogueGain": analogic,
            "ExposureTime": exposure,
            }
        )
    picam.configure(config)
    picam.start()
    
    return picam
    
if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 640
    CENTER_THRES = 50  # tolerância central
    RED_THRES_LOW = 200000
    RED_THRES_UPPER = 400000
    CIRCLE_THRES = 40
    NO_DET_LIMIT = 10
    
    last_circle = None
    circleHistory = None
    noDetCounter = 0

    # Carrega configuração da gpio
    pins_motors = Config.get("gpio")
    left_pins = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right_pins = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    # Inicia motores
    robot = Robot(left=left_pins, right=right_pins)

    # Centro do frame
    x_center = WIDTH // 2

    # Ganhos para controle proporcional
    Kp_rotate = 0.5
    Kp_forward = 0.3
    alpha = 0.2  # filtro exponencial
    prev_left = 0
    prev_right = 0
    max_delta = 20

    picam = cameraStart(HEIGHT, WIDTH)

    while True:
        frame = picam.capture_array()
        mask, _, _ = colorDualSegmentation(frame)
        hough, _ = houghDetect(mask)
        contorno = circleCannyDetect(mask)

        # Escolhe melhor detecção
        if hough is not None and contorno is not None:
            det = circleVoting(hough, contorno)
        elif hough is not None:
            det = hough
        elif contorno is not None:
            det = contorno
        else:
            det = None

        if det is not None:
            noDetCounter = 0
            if circleHistory is None or not inInterval(det, circleHistory, CIRCLE_THRES):
                circleHistory = list(det)
            else:
                # filtro exponencial
                circleHistory[0] = int(alpha * det[0] + (1 - alpha) * circleHistory[0])
                circleHistory[1] = int(alpha * det[1] + (1 - alpha) * circleHistory[1])
                circleHistory[2] = int(alpha * det[2] + (1 - alpha) * circleHistory[2])
            last_circle = circleHistory
        else:
            noDetCounter += 1
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None

        # Desenho e info na tela
        txt = "Nenhum circulo detectado"
        if circleHistory:
            x, y, r = circleHistory
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
            txt = f"X={x}  Y={y}  R={r}"

        openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        openCv.imshow("Deteccao Final", frame)
        openCv.imshow("Mascara", mask)

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

        # Área vermelha
        red_area = openCv.countNonZero(mask)

        if circleHistory is None:
            if red_area >= RED_THRES_LOW and RED_THRES_UPPER > red_area:
                robot.stop()
            elif last_circle:
                last_x, last_y, last_r = last_circle
                robot.move(60 if last_x > WIDTH // 2 else -60, -60 if last_x > WIDTH // 2 else 60)
            else:
                robot.move(-60, 60)
            continue

        # Controle proporcional
        x, y, r = circleHistory
        error_x = x_center - x
        error_r = 50 - r  # raio desejado aproximado
        rotate_speed = int(max(min(Kp_rotate * error_x, 100), -100))
        forward_speed = int(max(min(Kp_forward * error_r, 100), 0))

        # Combina rotação e avanço
        left_final = rotate_speed + forward_speed
        right_final = -rotate_speed + forward_speed

        # Limita delta de velocidade
        left_final = max(min(left_final, prev_left + max_delta), prev_left - max_delta)
        right_final = max(min(right_final, prev_right + max_delta), prev_right - max_delta)

        robot.move(left_final, right_final)
        prev_left, prev_right = left_final, right_final

        time.sleep(0.05)

    picam.stop()
    openCv.destroyAllWindows()