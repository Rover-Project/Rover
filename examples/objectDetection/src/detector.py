import cv2
from pathlib import Path
from ultralytics import YOLO
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from .decision import ObjectDecision

class YoloDetectorApp:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        camera_configs = self.config.get("camera")
        
        self.height = 640
        self.width = 640
        self.center_cam = self.width / 2
        
        self.picam = Camera(self.height, self.width)
        self.picam.start()
        
        self.picam.set_saturation(camera_configs.get("saturation", 1))
        self.picam.set_brightness(camera_configs.get("brigh", 0.25))
        self.picam.set_contrast(camera_configs.get("contrast", 1))
        
        # Carrega o modelo a partir da raiz do exemplo
        model_path = config_path.parent / "yolov8n.pt"
        self.model = YOLO(str(model_path))
        self.model.export(format="ncnn")
        
        self.od = ObjectDecision(self.center_cam)
        self.target_objects = [0, 13, 24, 26, 39, 41, 56, 63, 64, 66, 67, 73]
        self.avoid_objects = [0, 13, 24, 26, 56, 63, 66, 67]
        self.persue_objects = [39, 41, 64, 73]

    def run(self):
        print("Iniciando detecção com YOLOv8. Pressione 'q' para sair.")
        while True:
            situation = "Not defined"
            frame = self.picam.get_frame()
            if frame is None:
                continue

            results = self.model.predict(frame, conf=0.5, classes=self.target_objects)

            try:
                noted_frame = frame  # Fallback caso não haja results processáveis
                for r in results:
                    noted_frame = results[0].plot()

                    inference_time = results[0].speed['inference']
                    fps = 1000 / inference_time if inference_time > 0 else 0
                    text = f'FPS: {fps:.1f}'

                    font = cv2.FONT_HERSHEY_COMPLEX
                    text_size = cv2.getTextSize(text, font, 1, 2)[0]
                    text_x = noted_frame.shape[1] - text_size[0] - 10
                    text_y = text_size[1] + 10

                    cv2.putText(noted_frame, text, (text_x, text_y), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

                    str_erro = "0"
                    for box in r.boxes:
                        coords = box.xyxy[0].tolist()
                        id = int(box.cls[0])

                        if not coords:
                            print("Nenhum objeto")
                            situation = "Nothing to do"
                            erro = 0
                            str_erro = str(erro)
                            continue

                        if id in self.avoid_objects:
                            avoid = True
                            erro = self.od.decision(coords, avoid)
                            str_erro = str(erro)
                            situation = "Avoid"
                            print(erro)
                        else:
                            avoid = False
                            situation = "Persue"
                            erro = self.od.decision(coords, avoid)
                            str_erro = str(erro)
                            print(erro)

                    cv2.putText(noted_frame, situation, (text_x, text_y + 60), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(noted_frame, str_erro, (text_x + 20, text_y + 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

                cv2.imshow("detection", noted_frame)

                if cv2.waitKey(1) == ord("q"):
                    break

            except Exception as e:
                print(f"Error: {e}")

    def cleanup(self):
        print("\nEncerrando câmera e modelo...")
        if self.picam:
            self.picam.cleanup()
        cv2.destroyAllWindows()
