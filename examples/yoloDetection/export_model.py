from ultralytics import YOLO

if __name__ == "__main__":
    
    model = YOLO("yolov8n.pt") # carrega o modelo pré-treinado
    
    # exporta o modelo de forma otimizada nor formato .onnx
    # preparado para imagens 320x320
    model.export(
        format="onnx",
        imgsz=320,
        dynamic=False
    )