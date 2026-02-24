import cv2
from ultralytics import YOLO
from pathlib import Path

model = YOLO("yolov8n.pt")

img_path = "test.jpg"

results = model(img_path, save=True, conf=0.25)

for result in results:
    annotated_img = result.plot()
    
    cv2.imshow("Resultado da Detecção", annotated_img)
    
    print("Pressione qualquer tecla para fechar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # cv2.imwrite("resultado_final.jpg", annotated_img)