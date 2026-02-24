import cv2
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from ultralytics import YOLO
from pathlib import Path

# Inicializando a câmera

HEIGHT = 640
WIDTH = 640

config = Config(path(__file__).parent / 'config.yaml')

camera_configs = config.get("camera")

picam = Camera(HEIGHT, WIDTH)
picam.start()

picam.set_saturation(camera_configs["saturations"])
picam.set_brightness(camera_configs["brigh"])
picam.set_contrast(camera_configs["contrast"])

model = YOLO("yolov8n.pt")

while True:
    frame = picam.get_frame()

    results = model(frame)

    noted_frame = results[0].plot()

    inference_time = results[0].speed['inference']
    fps = 1000 / inference_time 
    text = f'FPS: {fps:.1f}'

    font = cv2.FONT_HERSHEY_COMPLEX
    text_size =cv2,getTextSize(text, font, 1, 2)[0]
    text_x = noted_frame.shape[1] - text_size[0] - 10
    text_y = text_size[1] + 10

    cv2.putText(noted_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)




