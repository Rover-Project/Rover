import time
import board
import busio
from adafruit_pca9685 import PCA9685

from roverlib.plugins.camera.autoFocus import AfCamera
import cv2 as openCv

# Inicialização PCA9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# Controle dos servos
def set_servo_speed(channel: int, speed):
    min_pulse = 2000
    max_pulse = 8000
    neutral = 5000

    pulse = int(neutral + speed * (max_pulse - min_pulse) / 2)
    pulse = max(min_pulse, min(max_pulse, pulse))

    pca.channels[channel].duty_cycle = pulse

def stop(ch: int):
    set_servo_speed(ch, 0)

def forward(ch: int, speed):
    s = speed / 100
    set_servo_speed(ch, s)

def backward(ch: int, speed):
    s = speed / 100
    set_servo_speed(ch, -s)

# Programa principal
if __name__ == "__main__":
    HEIGHT = 1080
    WIDTH = 1080
    speed = 50  # 0–100
    
    servoVertival = 0
    servoHorizontal = 1


    # Inicializa câmera
    try:
        camera = AfCamera(HEIGHT, WIDTH)
        camera.start()
    except:
        raise RuntimeError("Erro ao abrir câmera")

    try:
        while True:
            frame = camera.get_frame()

            if frame is not None:
                openCv.imshow("Rover", frame)

                key = openCv.waitKey(10) & 0xFF

                if key == ord("w"):
                    forward(servoVertival, speed)

                elif key == ord("s"):
                    backward(servoVertival, speed)

                elif key == ord("a"):
                    forward(servoHorizontal, speed)

                elif key == ord("d"):
                    backward(servoHorizontal, speed)

                elif key == ord("e"):
                    speed = min(100, speed + 10)

                elif key == ord("r"):
                    speed = max(0, speed - 10)

                elif key == ord("q"):
                    break

                else:
                    stop(servoHorizontal)
                    stop(servoVertival)

                print(f"Velocidade: {speed}")

    except KeyboardInterrupt:
        print("Encerrando.")

    finally:
        stop(servoVertival)
        stop(servoHorizontal)
        pca.deinit()
        camera.cleanup()
        openCv.destroyAllWindows()