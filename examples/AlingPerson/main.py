from pathlib import Path
import time
import cv2 as opencv
import numpy
import onnxruntime as onnx
from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.plugins.PCAServos.pcaServos import PCAServos 

# Configurações do Modelo e Câmera
MODEL_PATH = Path(__file__).parent / "models" / "yolov8n.onnx"
IMAGE_SIZE = 320  # Resolução de entrada da YOLO
CONF_THRESHOLD = 0.4  # Limiar de confiança para detecção
HEIGHT = 640
WIDTH = 640
CLASS_INTEREST = {0: "Pessoa"}

SPEED = 50 # Velocidade padrao
SERVO_V = 1 # Servo vertival 
SERVO_H = 0 # Servo Horizontal
    

def get_cpu_temp():
    """Lê a temperatura atual da CPU na Raspberry Pi 5 através do sistema de arquivos do Linux."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            # O valor vem em miligraus Celsius 
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0


if __name__ == "__main__":
    providers = ["CPUExecutionProvider"]  # Força execução na CPU

    model_session = onnx.InferenceSession(MODEL_PATH, providers=providers)
    input_name = model_session.get_inputs()[0].name

    # Inicia câmera 
    camera = AfCamera(height=HEIGHT, width=WIDTH)
    camera.start()
    
    # Inicia servos 
    servos = PCAServos()

    while True:
        frame = camera.get_frame()

        if frame is not None:
            start_time = time.time()
            HEIGHT, WIDTH = frame.shape[:2]

            # valores padrões se nenhuma pessoa for detectada
            c_x, c_y = WIDTH // 2, HEIGHT // 2

            # Redimensiona para 320x320 e converte BGR para RGB
            img = opencv.resize(
                frame, (IMAGE_SIZE, IMAGE_SIZE), opencv.INTER_CUBIC
            )
        
            # Normalização [0,1] e adequação de dimensões
            input_tensor = img.astype(numpy.float32) / 255.0
            input_tensor = numpy.transpose(input_tensor, (2, 0, 1))
            input_tensor = numpy.expand_dims(input_tensor, axis=0)

            # Inferência 
            results = model_session.run(None, {input_name: input_tensor})[0]
            predictions = numpy.squeeze(results).T

            boxes = []
            confidences = []
            class_ids = []

            # Fatores de escala para mapear de volta à dimensão original da imagem
            x_factor = WIDTH / IMAGE_SIZE
            y_factor = HEIGHT / IMAGE_SIZE

            # processamendo de boxs
            for prediction in predictions:
                scores = prediction[4:]
                class_id = numpy.argmax(scores)
                max_score = scores[class_id]

                if max_score >= CONF_THRESHOLD and class_id in CLASS_INTEREST:
                    cx, cy, w, h = (
                        prediction[0],
                        prediction[1],
                        prediction[2],
                        prediction[3],
                    )

                    left = int((cx - 0.5 * w) * x_factor)
                    top = int((cy - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(
                        h * y_factor
                    ) 

                    boxes.append([left, top, width, height])
                    confidences.append(float(max_score))
                    class_ids.append(class_id)

            # Aplicação de NMS (Non-Maximum Suppression)
            indices = opencv.dnn.NMSBoxes(
                boxes, confidences, CONF_THRESHOLD, 0.45
            )

            array_x, array_y, array_w, array_h = [], [], [], []

            if len(indices) > 0:
                for detection in indices.flatten():
                    array_x.append(min(boxes[detection][0], WIDTH))
                    array_y.append(min(boxes[detection][1], HEIGHT))
                    array_w.append(min(boxes[detection][2], WIDTH))
                    array_h.append(min(boxes[detection][3], HEIGHT))

                min_x, min_y = min(array_x), min(array_y)
                max_x = min(max(array_w) + max(array_x), WIDTH)
                max_y = min(max(array_h) + max(array_y), HEIGHT)

                w = numpy.sqrt(numpy.pow(max_x - min_x, 2))
                h = numpy.sqrt(numpy.pow(max_y - min_y, 2))

                # Atualiza o centro com base nas detecções
                c_x = int(min_x + (w // 2))
                c_y = int(min_y + (h // 2))

                # Desenha o retângulo na área de interesse
                opencv.rectangle(
                    frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2
                )
                opencv.circle(frame, (c_x, c_y), 5, (0, 0, 255), -1)
                opencv.putText(
                    frame,
                    f"center: ({c_x},{c_y})",
                    (c_x, c_y - 10),
                    opencv.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )

            # Calculo de fps e temperatura
            fps = 1.0 / (time.time() - start_time)
            temp_cpu = get_cpu_temp()

            error_x = c_x - (WIDTH // 2)
            error_y = c_y - (HEIGHT // 2)
            
            info_text = f"FPS: {fps:.1f} | Temp: {temp_cpu:.1f}C | Err: ({error_x}, {error_y})"
            opencv.putText(
                frame,
                info_text,
                (20, 30),
                opencv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

            # Exibe o frame em tela
            opencv.imshow("Teste - YOLOv8 ONNX (Pi5)", frame)

            key = opencv.waitKey(1) & 0xFF
            
            if key == ord("w"):
                servos.forward(channels=tuple([SERVO_V]), speed=SPEED)

            elif key == ord("s"):
                servos.backward(channels=tuple([SERVO_V]), speed=SPEED)

            elif key == ord("a"):
                servos.forward(channels=tuple([SERVO_H]), speed=SPEED)

            elif key == ord("d"):
                servos.backward(channels=tuple([SERVO_H]), speed=SPEED)
                
            elif key == ord("q"):
                break
            
            else:
                servos.stop_all()


    camera.cleanup()
    opencv.destroyAllWindows()