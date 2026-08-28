from pathlib import Path
import time
import cv2 as opencv
import numpy
import onnxruntime as onnx

from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.plugins.PCAServos.pcaServos import PCAServos 
from roverlib.modules.movement.PID import PID

# Configurações do Modelo e Câmera
MODEL_PATH = Path(__file__).parent / "models" / "yolov8n.onnx"
IMAGE_SIZE = 320      # Resolução de entrada da YOLO
CONF_THRESHOLD = 0.4  # Limiar de confiança para detecção
HEIGHT = 640
WIDTH = 640
CLASS_INTEREST = {0: "Pessoa"}

SERVO_V = 1  # Servo vertical 
SERVO_H = 0  # Servo horizontal

# Configurações do Filtro e Deadzone
DEADZONE_X = 25
DEADZONE_Y = 25
SMOOTH_ALFA = 0.3

# Limites de quadros sem detecção
NO_DET_LIMIT = 10
SEARCH_SPEED = 0.08  # Velocidade do servo ao buscar a pessoa

# Parâmetros de Velocidade do Servo
MIN_SPEED = 0.03
MAX_SPEED = 0.20
MAX_RAMP_DELTA = 0.01

def get_cpu_temp():
    """Lê a temperatura atual da CPU na Raspberry Pi 5."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0

def smooth_signal(current, last, alpha=0.3):
    return alpha * current + (1 - alpha) * last


if __name__ == "__main__":
    providers = ["CPUExecutionProvider"]
    model_session = onnx.InferenceSession(MODEL_PATH, providers=providers)
    input_name = model_session.get_inputs()[0].name

    camera = AfCamera(height=HEIGHT, width=WIDTH)
    camera.start()
    
    servos = PCAServos()
    
    # Instância do PID para o Eixo Horizontal (X)
    pid_x = PID(kp=0.2, ki=0.055, kd=0.02, max_I=0.3, max_dt=0.5)

    # Inicialização das variáveis de estado
    last_error_x = None
    last_speed_h = 0.0
    no_det_counter = 0
    pause = True

    try:
        while True:
            frame = camera.get_frame()

            if frame is not None:
                start_time = time.time()
                HEIGHT, WIDTH = frame.shape[:2]
                x_center_img = WIDTH // 2
                
                norm_error_x = 0.0
                u_x = 0

                # Redimensiona para 320x320 e converte BGR para RGB
                img = opencv.resize(frame, (IMAGE_SIZE, IMAGE_SIZE), opencv.INTER_CUBIC)
            
                # Normalização e tensores
                input_tensor = img.astype(numpy.float32) / 255.0
                input_tensor = numpy.transpose(input_tensor, (2, 0, 1))
                input_tensor = numpy.expand_dims(input_tensor, axis=0)

                # Inferência 
                results = model_session.run(None, {input_name: input_tensor})[0]
                predictions = numpy.squeeze(results).T

                boxes = []
                confidences = []
                x_factor = WIDTH / IMAGE_SIZE
                y_factor = HEIGHT / IMAGE_SIZE

                # Processamento das bounding boxes
                for prediction in predictions:
                    scores = prediction[4:]
                    class_id = numpy.argmax(scores)
                    max_score = scores[class_id]

                    if max_score >= CONF_THRESHOLD and class_id in CLASS_INTEREST:
                        cx, cy, w, h = prediction[0], prediction[1], prediction[2], prediction[3]
                        left = int((cx - 0.5 * w) * x_factor)
                        top = int((cy - 0.5 * h) * y_factor)
                        width = int(w * x_factor)
                        height = int(h * y_factor)

                        boxes.append([left, top, width, height])
                        confidences.append(float(max_score))

                # NMS
                indices = opencv.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, 0.45)

                detection_found = False
                c_x = x_center_img

                if len(indices) > 0:
                    detection_found = True
                    no_det_counter = 0

                    array_x, array_y, array_w, array_h = [], [], [], []
                    for detection in indices.flatten():
                        array_x.append(min(boxes[detection][0], WIDTH))
                        array_y.append(min(boxes[detection][1], HEIGHT))
                        array_w.append(min(boxes[detection][2], WIDTH))
                        array_h.append(min(boxes[detection][3], HEIGHT))

                    min_x, min_y = min(array_x), min(array_y)
                    max_x = min(max(array_w) + max(array_x), WIDTH)
                    max_y = min(max(array_h) + max(array_y), HEIGHT)

                    w = max_x - min_x
                    h = max_y - min_y

                    c_x = int(min_x + (w // 2))
                    c_y = int(min_y + (h // 2))

                    opencv.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                    opencv.circle(frame, (c_x, c_y), 5, (0, 0, 255), -1)
                else:
                    no_det_counter += 1

                # Lógica de erro e filtro (estilo motor DC)
                if detection_found:
                    raw_error_x = float(c_x - x_center_img)
                    
                    if abs(raw_error_x) < DEADZONE_X:
                        raw_error_x = 0.0

                    smoothed_x = raw_error_x if last_error_x is None else smooth_signal(raw_error_x, last_error_x, SMOOTH_ALFA)
                    last_error_x = smoothed_x

                    norm_error_x = smoothed_x / (WIDTH / 2.0)
                    u_x = pid_x.computer(norm_error_x)
                else:
                    # Se ultrapassar o limite de frames sem detecção, limpa os acumuladores do PID
                    if no_det_counter >= NO_DET_LIMIT:
                        pid_x.reset()
                        norm_error_x = 0.0
                        u_x = 0.0

                # Atuação no Servo Pan (Horizontal)
                if not pause:
                    if detection_found:
                        if abs(norm_error_x) == 0.0:
                            target_speed = 0.0
                        else:
                            raw_speed = abs(u_x)
                            target_speed = MIN_SPEED + (raw_speed * (MAX_SPEED - MIN_SPEED))
                            target_speed = min(MAX_SPEED, max(MIN_SPEED, target_speed))

                        # Rampa de aceleração/desaceleração
                        speed_delta = target_speed - last_speed_h
                        speed_delta = max(-MAX_RAMP_DELTA, min(MAX_RAMP_DELTA, speed_delta))
                        speed_h = last_speed_h + speed_delta
                        last_speed_h = speed_h

                        if speed_h < 0.01:
                            servos.stop(channels=tuple([SERVO_H]))
                        else:
                            if u_x < 0:
                                servos.forward(channels=tuple([SERVO_H]), speed=speed_h)
                            else:
                                servos.backward(channels=tuple([SERVO_H]), speed=speed_h)
                    else:
                        # Modo de busca quando perde o alvo (gira para o último lado conhecido)
                        if last_error_x is not None and last_error_x > 0:
                            servos.backward(channels=tuple([SERVO_H]), speed=SEARCH_SPEED)
                        else:
                            servos.forward(channels=tuple([SERVO_H]), speed=SEARCH_SPEED)
                        last_speed_h = SEARCH_SPEED
                else:
                    servos.stop(channels=tuple([SERVO_H]))
                    pid_x.reset()
                    last_speed_h = 0.0

                # Telemetria na Tela
                fps = 1.0 / (time.time() - start_time)
                temp_cpu = get_cpu_temp()
                info_text = f"FPS: {fps:.1f} | Temp: {temp_cpu:.1f}C | ErrX: {norm_error_x:.2f} | PID_X: {u_x:.2f}"
                opencv.putText(frame, info_text, (20, 30), opencv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                opencv.imshow("YOLOv8 Servo Pan-Tilt (Pi5)", frame)

                key = opencv.waitKey(10) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("p"):
                    servos.stop(channels=tuple([SERVO_V, SERVO_H]))
                    pause = True
                elif key == ord("c"):
                    pause = False

    finally:
        servos.stop(channels=tuple([SERVO_V, SERVO_H]))
        camera.cleanup()
        opencv.destroyAllWindows()