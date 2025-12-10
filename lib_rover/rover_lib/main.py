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

    # Ajuste de exposição
    # picam.set_controls({
    #     "AnalogueGain": 1.5,   # controla amplificação do sensor, <1 = mais escuro
    #     "ExposureTime": 30000, # em microssegundos, menor = mais escuro
    # })
    # picam.start()

    circleHistory = None  # média acumulada
    cont = 0
    LIMIAR = 20  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 20  # número máximo de frames sem detecção
    noDetCounter = 0

    pins_motors = Config.get("gpio")

    letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    robot = Robot(
        left=letf,
        right=right
    )

    x_center = {
        "low": (HEIGHT // 2) - THRES,
        "high": (HEIGHT // 2) + THRES
    }

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
                circleHistory = list(det)  # converte tupla para lista
                cont = 1
            else:
                # acumula valores
                circleHistory[0] += det[0]
                circleHistory[1] += det[1]
                circleHistory[2] += det[2]
                cont += 1
        else:
            noDetCounter += 1
            # se muitos frames sem detecção, zera histórico
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None
                cont = 0

        txt = "Nenhum circulo detectado"
        if circleHistory and cont > 0:
            # calcula média real
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

        if circleHistory is None:
            print("Nenhum circulo foi detectado")
            robot.move(-SPEED * 0.5, SPEED)  # Rotaciona procurando um círculo

        else:
            x, y, r = circleHistory  # Agora circles[0] já contém (x, y, r)
            print(f"Circulo unico detectado: centro - ({x}, {y}); raio - {r}")
            print(f"Tentando achar o centro: ({x_center['low']},{x_center['high']})")

            if x > x_center["high"]:
                robot.move(SPEED * 40, -SPEED)

            elif x < x_center["low"]:
                robot.move(-SPEED * 40, SPEED)
            else:
                robot.stop()

        time.sleep(0.5)

    picam.stop()
    openCv.destroyAllWindows()