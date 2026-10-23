import cv2 as openCv
import numpy as np
from pathlib import Path
from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera

class CircleFollower:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        
        # Parâmetros de Câmera e Imagem
        self.height = 640
        self.width = 640
        self.x_center = self.width // 2
        self.max_r = min(self.width, self.height) // 2
        
        # Inicia a Câmera
        self.camera = Camera(self.height, self.width)
        camera_configs = self.config.get("camera")
        self.camera.set_saturation(camera_configs.get("saturation", 1))
        self.camera.set_brightness(camera_configs.get("brigh", 0.25))
        self.camera.set_contrast(camera_configs.get("contrast", 1))
        
        # Inicia os Motores
        motor_config = self.config.get("gpio")["motor"]
        self.robot = Robot(
            left=motor_config["left"],
            right=motor_config["right"],
            calibration=Calibration(
                right=motor_config["calibration"]["right"],
                left=motor_config["calibration"]["left"]
            )
        )
        
        # Parâmetros de Controle PID
        self.r_speed_base = 60
        self.x_speed_base = 40
        self.pid_x = PID(kp=(self.x_speed_base / self.x_center), ki=1, kd=1)
        self.pid_r = PID(kp=(self.r_speed_base / self.max_r), ki=1, kd=1)
        
        # Constantes de Estado
        self.search_speed = 70
        self.thres_red = 350_000
        self.circle_thres = 40
        self.no_det_limit = 10
        
        # Variáveis de Estado
        self.have_detect = False
        self.circle_history = None
        self.counter_history = 0
        self.no_det_counter = 0
        self.pause = True
        self.error_x = 0

    @staticmethod
    def voting(hough: np.ndarray, contour: np.ndarray, thres_xy: int = 20, thres_r: float = 0.3) -> np.ndarray:
        if abs(np.sum(hough[:2] - contour[:2])) < thres_xy:
            if abs(hough[2] - contour[2]) < (hough[2] * thres_r):
                return (hough + contour) // 2
        return contour

    @staticmethod
    def in_interval(v1: np.ndarray, v2: np.ndarray, thres: float) -> bool:
        return abs(np.sum(v1 - v2)) <= thres

    def run(self):
        try:
            self.camera.start()
            print("Sistema iniciado. Pressione 'c' para começar, 'p' para pausar, e 'q' para sair.")
        except Exception as e:
            raise RuntimeError(f"Erro ao iniciar a câmera: {e}")

        while True:
            frame = self.camera.get_frame()
            if frame is None:
                continue

            mask = ProcessingImage.color_dual_segmentation(frame)
            hough, _ = VisionModule.houghCircleDetect(mask)
            contour = VisionModule.circleCannyDetect(mask)

            hough = np.array(hough) if hough is not None else None
            contour = np.array(contour) if contour is not None else None

            det = None
            if hough is not None and contour is not None:
                det = self.voting(hough, contour)
            elif hough is not None:
                det = hough
            elif contour is not None:
                det = contour

            if det is not None:
                self.no_det_counter = 0
                self.have_detect = True
                
                if self.circle_history is None or not self.in_interval(det, self.circle_history, self.circle_thres):
                    self.circle_history = det.copy()
                    self.counter_history = 1
                else:
                    self.circle_history = (det + self.circle_history) // 2
                    self.counter_history += 1
            else:
                self.no_det_counter += 1
                if self.no_det_counter >= self.no_det_limit:
                    self.circle_history = None
                    self.counter_history = 0

            txt = "Nenhum circulo detectado"
            left, right = 0, 0

            if self.circle_history is not None:
                x, y, r = self.circle_history
                self.error_x = x - self.x_center
                error_r = r - self.max_r

                if r < 100:
                    speed_x = self.pid_x.controller_P(abs(self.error_x))
                    speed_r = self.pid_r.controller_P(abs(error_r)) if r <= self.max_r - 60 else 0
                    
                    right = speed_x + speed_r if self.error_x < 0 else speed_r
                    left = speed_x + speed_r if self.error_x > 0 else speed_r

                openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
                openCv.circle(frame, (x, y), 3, (0, 0, 255), -1)
                txt = f"Err X: {self.error_x} | Err R: {error_r} | R: {r}"

            openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            openCv.imshow("Deteccao Final", frame)
            openCv.imshow("Mascara", mask)

            key = openCv.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key == ord("p"):
                self.pause = True
                print("Sistema Pausado")
            elif key == ord("c"):
                self.pause = False
                print("Sistema Ativo")

            red_area = openCv.countNonZero(mask)

            if not self.pause:
                if self.circle_history is None:
                    if not self.have_detect:
                        self.robot.turn_right(self.search_speed)
                    elif red_area >= self.thres_red:
                        self.robot.stop()
                    else:
                        if self.error_x > 0:
                            self.robot.turn_left(self.search_speed)
                        else:
                            self.robot.turn_right(self.search_speed)
                else:
                    self.robot.move(speed_left=left, speed_right=right)
            else:
                self.robot.stop()

    def cleanup(self):
        print("\nDesligando o sistema...")
        self.robot.cleanup()
        self.camera.cleanup()
        openCv.destroyAllWindows()