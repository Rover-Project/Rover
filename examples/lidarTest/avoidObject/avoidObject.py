from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.lidar.lidar import Lidar
import cv2 as openCv
import time
from pathlib import Path

HEIGHT = 640 # Altura da imagem 
WIDTH = 640 # Largura da imagem
x_center = WIDTH / 2
max_dist = 30 # Distancia maxima para o Rover parar (em cm)
min_dist = 100 # Distancia minima para tomada de atitude (em cm)
dist_history = []
dist_limit = 30
X_SPEED = 50 # Velocidade para controle direcional no eixo X
SEARCH_SPEED = 70 # Velocidade de busca
left_speed = X_SPEED # Velocidade do motor esquerdo
right_speed = X_SPEED # Velocidade do motor direito
avoid_type = "only" # or "both"
last_attempt = None # Flag para registrar o ultimo lado em que o Rover tentou achar uma saida

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
    kp=(X_SPEED / max_dist),  # constante de normalização para a velociade de controle x
    ki=1, 
    kd=1
)

# Funcao de tomada de decisao do Rover a partir do Lidar e/ou da Picam
def decide(dist: float, no_way: bool):
        global last_attempt
        global min_dist
        global max_dist
        global left_speed
        global right_speed
        global X_SPEED

        if dist <= 0: 
            return no_way

        # --- CASO 1 - CAMINHO LIVRE---
        # Rover esta muito longe de qualquer objeto (segue em frente)
        if dist > min_dist:
            print("Caso 1")
            left_speed = X_SPEED # Reinicia previamente a velocidade dos motores esquerdo e direito
            right_speed = X_SPEED # Antes de entrar no CASO 2 novamente
            last_attempt = None
            print("Caminho livre a frente")
            robot.forward(X_SPEED)
            #robot.move(70,70)
            return False
            
        # --- CASO 2 - APROXIMAÇÃO --- 
        # O Rover nao esta muito longe do objeto, mas tambem nao esta muito perto
        if dist < min_dist and dist > max_dist:
            print("Caso 2")
            error_dist = max_dist - dist

            correction = pid_x.controller_PID(error_dist)

            if last_attempt is None:
                last_attempt = "right"
            
            if last_attempt == "right":
                l_val = X_SPEED + correction
                r_val = X_SPEED - correction
            else:
                l_val = X_SPEED - correction
                r_val = X_SPEED + correction

            left_speed = max(0, min(90, left_speed))
            right_speed = max(0, min(90, right_speed))

            print(f"Possivel objeto se aproximando em {dist} cm. Reduzindo")
            robot.move(left_speed, right_speed)
            return False
        
        # --- CASO 3 - OBJETO A FRENTE --- 
        # Distancia maxima entre o Rover e a superficie alcancada (muito perto)
        if dist <= max_dist:
            # Para o Rover e faz ele tomar um pouco de distancia da superfice
            print("Caso 3")
            robot.stop()
            time.sleep(4)
            robot.backward(duration=2.3)
            time.sleep(0.1)

            robot.turn_degrees(90)
            time.sleep(0.2)
            robot.stop()

            new_dist, _, _ = lidar.get_read()
            if new_dist > dist and new_dist > max_dist:
                print("Caminho Livre")
                robot.forward()
                return False
            
            else:
                robot.turn_degrees(-180)
                time.sleep(0.2)
                robot.stop()

            new_dist, _, _ = lidar.get_read()
            if new_dist > dist and new_dist > max_dist:
                print("Caminho livre a Esquerda")
                robot.forward()
                return False
            
            else:
                print("Beco sem saida")
                return True # Boolean para uma variavel chamada no_ways_to go
            
            # --- CASO 4 - SEM SAIDA ---
        # Logica extrema para fazer o Rover encontrar um caminho
        if no_way:
            robot.stop()
            robot.backward(duration=2)
            robot.turn_degrees(180)
            return False
        
        print("Não decidiu nada")
        return False
        
def avoidObject(avoid_type: str):
    """
    Funcao principal para capacitar o Rover a detectar e desviar de objetos
    ecolhendo a melhor rota
    """
    no_way = False
    while True:
        try:
            if avoid_type == "both":
                frame = picam.get_frame()

            dist, stren, temp = lidar.get_read()
            print(dist)
            
            if len(dist_history) > dist_limit:
                dist_history.pop(0)

                average_dist = sum(dist_history) / len(dist_history)
                # Se a distância média é baixa e a variação é mínima, ele provavelmente bateu
                if average_dist < max_dist and abs(average_dist - dist) < 1.0:
                    no_way = True

            dist_history.append(dist)
                
            if dist <= 0: 
                print("Nenhuma distância recebida")

            else:
                no_way = decide(dist, no_way)
        
        except (KeyboardInterrupt, Exception) as e:
            print(f"Error: {e}")
            break

    robot.cleanup()

    try:
        picam.cleanup()
    except Exception as e:
        print("Camera não inicializada")
