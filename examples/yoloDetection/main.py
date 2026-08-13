
import cv2 as opencv
import numpy
import onnxruntime as onnx
from pathlib import Path
import time
from roverlib.plugins.camera.camera import Camera

MODEL_PAHT = Path(__file__).parent / "models" / "yolov8n.onnx" # path do modelo
IMAGE_SIZE = 320 # proporção da imagem
CONF_THRESHOLD = 0.4 # limiar de confiança para a detecçao
HEIGHT = 640
WIDTH = 640

CLASS_INTEREST = {0: "Pessoa", 39: "Garrafa", 56: "Cadeira"}

if __name__ == "__main__":
    providers = ["CPUExecutionProvider"] # Força execução na CPU
    
    model_session = onnx.InferenceSession(
        MODEL_PAHT,
        providers=providers
    )

    input_name = model_session.get_inputs()[0].name
    
     # Inicia câmera
    camera = Camera(HEIGHT, WIDTH) 
    camera.start()
    
    while True:
        
        frame = camera.get_frame() # ler frame 
        
        if frame is not None:
            
            start_time = time.time()
            h_origin, w_origin = frame.shape[:2] 
            
            # ajusta o tamanho da imagem para 320x320 e trasforma o espaco de cores
            img = opencv.resize(frame, (IMAGE_SIZE, IMAGE_SIZE), opencv.INTER_CUBIC)
            img = opencv.cvtColor(img, opencv.COLOR_BGR2RGB)
            
            # normaliza para o intervalo [0,1]
            input_tensor = img.astype(numpy.float32) / 255.0 
            input_tensor = numpy.transpose(input_tensor, (2, 0, 1))
            input_tensor = numpy.expand_dims(input_tensor, axis=0)
            
            # Inferência do modelo
            results = model_session.run(None, {input_name: input_tensor})[0]
            
            predictions = numpy.squeeze(results).T
            
            boxes = []
            confidences = []
            class_ids = []
            
            x_factor = w_origin / IMAGE_SIZE
            y_factor = h_origin / IMAGE_SIZE
        
            for prediction in predictions:
                scores = prediction[4:]
                class_id = numpy.argmax(scores)
                max_score = scores[class_id]
                
                if max_score >= CONF_THRESHOLD and class_id in CLASS_INTEREST:
                    cx, cy, w, h = prediction[0], prediction[1], prediction[2], prediction[3]
                    
                    # ajusta as coordenadas para o tamanho original do frame
                    left = int((cx - 0.5 * w) * x_factor)
                    top = int((cy - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * x_factor)

                    boxes.append([left, top, width, height])
                    confidences.append(float(max_score))
                    class_ids.append(class_id)
            
            indices = opencv.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, 0.45)

            if len(indices) > 0:
                for detection in indices.flatten():
                    x, y, w, h = boxes[detection]
                    cls_id = class_ids[detection]
                    label = f"{CLASS_INTEREST[cls_id]}: {confidences[detection]:.2f}"
                    
                    # calcula o centroide
                    center_x = x + (w // 2)
                    center_y = y + (h // 2)
                    
                    # desenha caixa e ponto central no objeto
                    opencv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    opencv.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                    opencv.putText(frame, label, (x, y - 10), opencv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # calcula a quantidade de fps        
            fps = 1.0 / (time.time() - start_time)
            opencv.putText(frame, f"FPS (CPU): {fps:.1f}", (20, 40), opencv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            opencv.imshow("Teste - YOLOv8 ONNX (Pi5)", frame)
            
            if opencv.waitKey(1) & 0xFF == ord('q'):
                break
            
    camera.release()
    opencv.destroyAllWindows()