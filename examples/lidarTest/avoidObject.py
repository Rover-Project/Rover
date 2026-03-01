from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.lidar.lidar import Lidar
from .avoidDecision  import Decision
import cv2 as openCv
from pathlib import Path

X_SPEED = 40 # Velocidade para controle direcional no eixo X
SEARCH_SPEED = 70
HEIGHT = 640 # Altura da imagem 
WIDTH = 640 # Largura da imagem
x_center = WIDTH / 2
avoid_type = "only" # or "both"
max_dist = 40 # Distancia maxima para o Rover nao parar (em cm)
min_dist = 150 # Distancia minima para tomada de atitude (em cm)

# --- CONFIG SECTION ---
config = Config(Path(__file__).parent / "config.yaml")

picam = None

if avoid_type == "both":
    camera_configs = config.get("camera")

    # Iniciando a camera
    picam = Camera(HEIGHT, WIDTH)
    picam.start()
    # Configuração da câmera
    picam.set_saturation(camera_configs["saturation"])
    picam.set_brightness(camera_configs["brigh"])
    picam.set_contrast(camera_configs["contrast"])

# Iniciando o lidar
lidar = Lidar()
lidar.start()

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

# Funcao de tomada de decisao do Rover a partir do Lidar e/ou da Picam
def decide(dist: float, strengh:float, temp:float):
        # Distancia entre o Rover e a superficie alcancada (muito perto)

        if dist > min_dist:
            print("Caminho livre a frente")
            return "Em frente" # <- Direcao livre

        if dist <= max_dist:
            robot.stop()
            robot.turn_degrees(-90)
            left_dist, stren, _ = lidar.get_read()
            
            robot.turn_degrees(180)
            right_dist, stren, _ = lidar.get_read()

            # Caso seja necessario recuar antes de fazer a curva e desviar do objeto
            # robot.move(-40, -40, 1)

            if left_dist > right_dist:
                robot.turn_degrees(-180)
                robot.move(X_SPEED, X_SPEED)
                return "Esquerda" # <- Lado livre
            
            else: 
                robot.move(X_SPEED, X_SPEED)
                return "Direita" # <- Lado livre

        if dist < min_dist and dist > max_dist:
            print("Nao implementei ainda")
            pass
def avoidObject(avoid_type: str):
    """
    Funcao principal para capacitar o Rover a detectar e desviar de objetos
    ecolhendo a melhor rota para tal

    Args:
        avoid_type (string): only => only lidar | both => lidar and camera
    """
    
    while True:
        try:
            if avoid_type == "both":
                frame = picam.get_frame()

            dist, stren, temp = lidar.get_read()
            print(f" TESTE: {dist}")
            if not dist:
                print("Nenhuma distancia recebida")
            
            decide(dist, stren, temp)
        
        except KeyboardInterrupt or Exception as e:
            break

    robot.cleanup()
    picam.cleanup()
    openCv.destroyAllWindows()