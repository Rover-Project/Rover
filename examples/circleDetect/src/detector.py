import cv2 as openCv
import numpy as np
from pathlib import Path
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.utils.config_manager import Config
from roverlib.plugins.camera.cameraInterface import CameraInterface

class CircleDetector:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        self.camera = self._init_camera()
        
        # Parâmetros de Estado
        self.circle_history = None
        self.limiar = 20
        self.no_det_limit = 20
        self.no_det_counter = 0

    def _init_camera(self) -> CameraInterface:
        cam_config = self.config.get("camera")
        h = cam_config.get("resolution", {}).get("h", 640)
        w = cam_config.get("resolution", {}).get("w", 640)
        fps = cam_config.get("fps", 30)

        # Tentativa 1: Câmara com Autofoco (Picamera2)
        try:
            from roverlib.plugins.camera.autoFocus import AfCamera, AfModeEnum
            cam = AfCamera(height=h, width=w, fps=fps, horizontalFlip=True, verticalFlip=True, afMode=AfModeEnum.Continuous)
            cam.start()
            cam.set_brightness(cam_config.get("brigh", 0.25))
            cam.set_contrast(cam_config.get("contrast", 1))
            cam.set_saturation(cam_config.get("saturation", 1))
            print("Câmara Autofoco (Picamera2) iniciada.")
            return cam
        except Exception:
            pass

        # Tentativa 2: Câmara Fixa (Picamera2)
        try:
            from roverlib.plugins.camera.camera import Camera
            cam = Camera(height=h, width=w, fps=fps)
            cam.start()
            cam.set_brightness(cam_config.get("brigh", 0.25))
            cam.set_contrast(cam_config.get("contrast", 1))
            cam.set_saturation(cam_config.get("saturation", 1))
            print("Câmara Fixa (Picamera2) iniciada.")
            return cam
        except Exception:
            pass

        # Tentativa 3: Webcam (Fallback PC)
        try:
            from roverlib.plugins.camera.webcam import Webcam
            cam = Webcam(height=h, width=w)
            cam.start()
            print("Webcam iniciada.")
            return cam
        except Exception as e:
            raise RuntimeError(f"Nenhuma câmara pôde ser iniciada: {e}")

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
        print("Iniciando deteção de círculos. Pressione 'q' para sair.")
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                continue

            mask = ProcessingImage.color_dual_segmentation(frame, gamma=1.9)
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
                if self.circle_history is None or not self.in_interval(det, self.circle_history, self.limiar):
                    self.circle_history = det.copy()
                else:
                    self.circle_history = (det + self.circle_history) // 2
            else:
                self.no_det_counter += 1
                if self.no_det_counter >= self.no_det_limit:
                    self.circle_history = None

            txt = "Nenhum circulo detectado"
            if self.circle_history is not None:
                x, y, r = self.circle_history
                openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
                openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
                txt = f"X={x}  Y={y}  R={r}"

            openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            openCv.imshow("Deteccao Final", frame)
            openCv.imshow("Mascara", mask)

            if openCv.waitKey(10) & 0xFF == ord('q'):
                break

    def cleanup(self):
        print("\nA encerrar o sistema de visão...")
        self.camera.cleanup()
        openCv.destroyAllWindows()