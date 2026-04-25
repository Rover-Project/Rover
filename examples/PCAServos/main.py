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
def set_servo_speed(channel, speed):
    min_pulse = 2000
    max_pulse = 8000
    neutral = 5000

    pulse = int(neutral + speed * (max_pulse - min_pulse) / 2)
    pulse = max(min_pulse, min(max_pulse, pulse))

    pca.channels[channel].duty_cycle = pulse

# Motores (canal 0 = esquerdo, 1 = direito)
def stop():
    set_servo_speed(0, 0)
    set_servo_speed(1, 0)

def forward(speed):
    s = speed / 100
    set_servo_speed(0, s)
    set_servo_speed(1, s)

def backward(speed):
    s = speed / 100
    set_servo_speed(0, -s)
    set_servo_speed(1, -s)

def turn_left(speed):
    s = speed / 100
    set_servo_speed(0, -s)
    set_servo_speed(1, s)

def turn_right(speed):
    s = speed / 100
    set_servo_speed(0, s)
    set_servo_speed(1, -s)

# Programa principal
if __name__ == "__main__":
    HEIGHT = 640
    WIDTH = 640
    speed = 50  # 0–100

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
                    forward(speed)

                elif key == ord("s"):
                    backward(speed)

                elif key == ord("a"):
                    turn_left(speed)

                elif key == ord("d"):
                    turn_right(speed)

                elif key == ord("e"):
                    speed = min(100, speed + 10)

                elif key == ord("r"):
                    speed = max(0, speed - 10)

                elif key == ord("q"):
                    break

                else:
                    stop()

                print(f"Velocidade: {speed}")

    except KeyboardInterrupt:
        print("Encerrando.")

    finally:
        stop()
        pca.deinit()
        camera.cleanup()
        openCv.destroyAllWindows()