import cv2 as opencv # type: ignore
from ultralytics import YOLO # type: ignore

model = YOLO("yolov8n.pt")

from pathlib import Path

# Descobre a pasta onde este script está salvo
script_dir = Path(__file__).parent

# Monta o caminho para a foto na mesma pasta do script
img_path = str(script_dir / "foto.jpg")

results = model(img_path, save=True, conf=0.25)

dimensions = (640, 640)

for result in results:
    annotated_img = result.plot()
    
    resized_img = opencv.resize(annotated_img, dimensions, interpolation=opencv.INTER_AREA)

    opencv.imshow("Resultado da Detecção", resized_img)
    
    print("Pressione qualquer tecla para fechar...")
    opencv.waitKey(0)
    opencv.destroyAllWindows()

    # opencv.imwrite("resultado_final.jpg", annotated_img)