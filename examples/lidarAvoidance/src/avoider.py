import time
import cv2 as openCv
from pathlib import Path
from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.lidar.lidar import Lidar

class ObstacleAvoider:
    def __init__(self, config_path: Path, avoid_type: str = "only"):
        self.config = Config(config_path)
        self.avoid_type = avoid_type
        
        # Constantes de Estado
        self.height = 640
        self.width = 640
        self.x_center = self.width / 2
        self.max_dist = 30
        self.min_dist = 100
        self.x_speed = 60
        self.search_speed = 70
        
        # Variáveis de Controle
        self.dist_history = []
        self.dist_history_limit = 30
        self.left_speed = self.x_speed
        self.right_speed = self.x_speed
        self.last_attempt = None
        
        # Inicialização da Câmera (se "both")
        self.picam = None
        if self.avoid_type == "both":
            camera_configs = self.config.get("camera")
            try:
                self.picam = Camera(self.height, self.width)
                self.picam.start()
                self.picam.set_saturation(camera_configs.get("saturation", 1))
                self.picam.set_brightness(camera_configs.get("brigh", 0.25))
                self.picam.set_contrast(camera_configs.get("contrast", 1))
            except Exception as e:
                print(f"Aviso: Não foi possível iniciar a câmera: {e}")

        # Inicialização do Lidar
        self.lidar = Lidar()
        self.lidar.start()

        # Inicialização dos Motores
        motor_config = self.config.get("gpio")["motor"]
        self.robot = Robot(
            left=motor_config["left"], 
            right=motor_config["right"],
            calibration=Calibration(
                right=motor_config["calibration"]["right"],
                left=motor_config["calibration"]["left"]
            )
        )

        # Controlador PID
        self.pid_x = PID(
            kp=(self.x_speed / self.max_dist), 
            ki=1, 
            kd=1
        )

    def _decide(self, dist: float, no_way: bool):
        if dist <= 0: 
            return no_way

        # --- CASO 1 - CAMINHO LIVRE ---
        if dist > self.min_dist:
            # print("Caso 1")
            self.left_speed = self.x_speed 
            self.right_speed = self.x_speed 
            self.last_attempt = None
            print("Caminho livre a frente")
            self.robot.forward(self.x_speed)
            return False
            
        # --- CASO 2 - APROXIMAÇÃO --- 
        if self.max_dist < dist < self.min_dist:
            # print("Caso 2")
            error_dist = self.max_dist - dist
            correction = self.pid_x.controller_PID(error_dist)

            if self.last_attempt is None:
                self.last_attempt = "right"
            
            if self.last_attempt == "right":
                l_val = self.x_speed + correction
                r_val = self.x_speed - correction
            else:
                l_val = self.x_speed - correction
                r_val = self.x_speed + correction

            self.left_speed = max(0, min(90, l_val))
            self.right_speed = max(0, min(90, r_val))

            print(f"Possivel objeto se aproximando em {dist} cm. Reduzindo")
            self.robot.move(self.left_speed, self.right_speed)
            return False
        
        # --- CASO 3 - OBJETO A FRENTE --- 
        if dist <= self.max_dist:
            # print("Caso 3")
            self.robot.stop()
            time.sleep(1.7)
            self.robot.backward(duration=3)
            time.sleep(0.1)

            self.robot.turn_degrees(0.15)
            time.sleep(0.2)
            self.robot.stop()

            new_dist, _, _ = self.lidar.get_read()
            if new_dist > dist and new_dist > self.max_dist:
                print("Caminho Livre")
                self.robot.forward()
                return False
            else:
                self.robot.turn_degrees(-0.35)
                time.sleep(0.2)
                self.robot.stop()

            new_dist, _, _ = self.lidar.get_read()
            if new_dist > dist and new_dist > self.max_dist:
                print("Caminho livre a Esquerda")
                self.robot.forward()
                return False
            else:
                print("Beco sem saida")
                return True 
            
        # --- CASO 4 - SEM SAIDA ---
        if no_way:
            self.robot.stop()
            self.robot.turn_degrees(0.15)
            self.robot.forward(duration=2)

            new_dist, _, _ = self.lidar.get_read()
            if new_dist > dist and new_dist > self.max_dist:
                print("Caminho livre à Direita")
                self.robot.forward()
                return False
            else:
                self.robot.turn_degrees(-0.35)
                new_dist, _, _ = self.lidar.get_read()
                if new_dist > dist and new_dist > self.max_dist:
                    print("Caminho livre a Esquerda")
                    self.robot.forward()
                    return False
            
            self.robot.turn_degrees(0.35)
            return False
        
        return False
        
    def run(self):
        print(f"Iniciando prevenção de colisões. Modo: {self.avoid_type}")
        no_way = False
        
        while True:
            try:
                if self.avoid_type == "both" and self.picam:
                    frame = self.picam.get_frame()

                dist, stren, temp = self.lidar.get_read()
                
                if len(self.dist_history) > self.dist_history_limit:
                    self.dist_history.pop(0)
                    average_dist = sum(self.dist_history) / len(self.dist_history)
                    
                    if average_dist == dist:
                        no_way = True

                self.dist_history.append(dist)
                
                if dist <= 0: 
                    print("Nenhuma distância recebida")
                else:
                    no_way = self._decide(dist, no_way)
        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                break

    def cleanup(self):
        print("\nDesligando o sistema...")
        self.robot.cleanup()
        try:
            self.lidar.stop()
        except Exception:
            pass
            
        if self.picam:
            try:
                self.picam.cleanup()
            except Exception:
                pass
