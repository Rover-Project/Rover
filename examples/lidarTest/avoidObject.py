from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.lidar.lidar import Lidar
import cv2 as openCv
from pathlib import Path

HEIGHT = 640 # Altura da imagem 
WIDTH = 640 # Largura da imagem
X_SPEED = 40 # Velocidade para controle direcional no eixo X
SEARCH_SPEED = 70
x_center = WIDTH / 2

def avoidObject(avoid_type: str):
    """
    Funcao principal para capacitar o Rover a detectar e desviar de objetos
    ecolhendo a melhor rota para tal

    Args:
        avoid_type (string): only => only lidar | both => lidar and camera
    """
    # --- CONFIG SECTION ---
    config = Config(Path(__file__).parent / "config.yaml")

    if avoid_type == "both":
        camera_configs = config.get("camera")

        # Iniciando a camera
        picam = Camera(HEIGHT, WIDTH)
        picam.start()

    # Iniciando o lidar
    lidar = Lidar()
    lidar.start()

    # Configuração da câmera
    picam.set_saturation(camera_configs["saturation"])
    picam.set_brightness(camera_configs["brigh"])
    picam.set_contrast(camera_configs["contrast"])

    motor_config = config.get("gpio")["motor"]
    
    robot = Robot(
        left=motor_config["left"], 
        right=motor_config["right"],
        calibration=Calibration(
            right=motor_config["calibration"]["right"],
            left=motor_config["calibration"]["left"]
        )
    )

    # Configura controlador PID para p eixo x
    pid_x = PID(
        kp=(X_SPEED / x_center),  # constante de normalização para a velociade de controle x
        ki=1, 
        kd=1
    )

    while True:
        dist, stren, temp = lidar.get_read()
        print(f" TESTE: {dist}")
        if not dist:
            print("Nenhuma distancia recebida")

    
    robot.cleanup()
    picam.cleanup()
    openCv.destroyAllWindows()