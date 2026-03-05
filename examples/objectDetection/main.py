from .objectDetection import ObjectDetection

import cv2
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from ultralytics import YOLO
from pathlib import Path

config = Config(Path(__file__).parent / 'config.yaml')

camera_configs = config.get("camera")

HEIGHT = 640
WIDTH = 640

picam = Camera(HEIGHT, WIDTH)
picam.start()

center_cam = WIDTH / 2

picam.set_saturation(camera_configs["saturation"])
picam.set_brightness(camera_configs["brigh"])
picam.set_contrast(camera_configs["contrast"])

model = YOLO("yolov8n.pt")

model.export(format="ncnn")

od = ObjectDetection(center_cam)
target_objects = [0, 13, 24, 26, 39, 41, 56, 63, 64, 66, 67, 73]

avoid_objects = [0, 13, 24, 26, 56, 63, 66, 67]
persue_objects = [39, 41, 64, 73]

if __name__ == "__main__":
    while True:
        situation = "Not defined"
        frame = picam.get_frame()

        results = model.predict(frame, conf=0.5, classes=target_objects)

        try:
            for r in results:
                noted_frame = results[0].plot()

                inference_time = results[0].speed['inference']
                fps = 1000 / inference_time 
                text = f'FPS: {fps:.1f}'

                font = cv2.FONT_HERSHEY_COMPLEX
                text_size =cv2.getTextSize(text, font, 1, 2)[0]
                text_x = noted_frame.shape[1] - text_size[0] - 10
                text_y = text_size[1] + 10

                cv2.putText(noted_frame, text, (text_x, text_y), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

                for box in r.boxes:
                    coords = box.xyxy[0].tolist()
                    id = int(box.cls[0])

                    if id in avoid_objects:
                        avoid = True
                        erro = od.decision(coords, avoid)
                        situation = "Avoid"
                        
                    else:
                        avoid = False
                        situation = "Persue"
                        error = od.decision(coords, avoid)
                    
                    cv2.putText(noted_frame, situation, (text_x, text_y + 30), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(noted_frame, erro, (text_x + 20, text_y + 30), font, 1, (0, 0, 255, 2, cv2.LINE_AA))

            cv2.imshow("detection", noted_frame)

            if cv2.waitKey(1) == ord("q"):
                break

        except Exception as e:
            print(f"Error: {e}")

    try:
        picam.cleanup()

    except Exception as e:
        print(f"Error: {e}")