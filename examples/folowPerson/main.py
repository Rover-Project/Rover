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
IMAGE_SIZE = 320  # Resolução de entrada da YOLO
CONF_THRESHOLD = 0.4  # Limiar de confiança para detecção
HEIGHT = 640
WIDTH = 640
CLASS_INTEREST = {0: "Pessoa"}

SERVO_V = 1  # Servo vertical 
SERVO_H = 0  # Servo horizontal

# Configurações do Filtro e Deadzone
DEADZONE = 25
SMOOTH_ALFA = 0.3

def get_cpu_temp():
    """Lê a temperatura atual da CPU na Raspberry Pi 5 através do sistema de arquivos do Linux."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
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
    
    # Instância do PID para o Eixo Horizontal (X)
    # Satura a saída no intervalo de velocidade do servo [-1.0, 1.0]
    pid_x = PID(kp=1.2, ki=0.01, kd=0.05, max_integral=0.5, max_dt=0.5)

    last_smoothed_error_x = None
    pause = True

    while True:
        frame = camera.get_frame()

        if frame is not None:
            start_time = time.time()
            HEIGHT, WIDTH = frame.shape[:2]

            # Valores padrões se nenhuma pessoa for detectada
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

            x_factor = WIDTH / IMAGE_SIZE
            y_factor = HEIGHT / IMAGE_SIZE

            # Processamento das bounding boxes
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
                    height = int(h * y_factor) 

                    boxes.append([left, top, width, height])
                    confidences.append(float(max_score))
                    class_ids.append(class_id)

            # NMS (Non-Maximum Suppression)
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

                c_x = int(min_x + (w // 2))
                c_y = int(min_y + (h // 2))

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

            # --- PROCESSAMENTO DO ERRO E PID (EIXO X) ---
            raw_error_x = c_x - (WIDTH // 2)

            # Filtro Passa-Baixas no erro bruto
            if last_smoothed_error_x is None:
                smoothed_error_x = float(raw_error_x)
            else:
                smoothed_error_x = (
                    SMOOTH_ALFA * raw_error_x + (1 - SMOOTH_ALFA) * last_smoothed_error_x
                )
            last_smoothed_error_x = smoothed_error_x

            # Deadzone
            error_x = 0.0 if numpy.abs(smoothed_error_x) < DEADZONE else smoothed_error_x

            # Normalização do Erro para [-1.0, 1.0]
            norm_error_x = error_x / (WIDTH / 2)

            # Cálculo do Sinal PID
            u_x = pid_x.compute(norm_error_x)

            # controle dos servos
            if not pause:
                if numpy.abs(error_x) == 0.0:
                    servos.stop(channels=tuple([SERVO_H]))
                else:
                    # u_x retorna entre -1.0 e 1.0
                    # speed em forward e backward deve ser a magnitude positiva [0.0 a 1.0]
                    speed_h = min(1.0, numpy.abs(u_x))

                    if u_x < 0:
                        servos.forward(channels=tuple([SERVO_H]), speed=speed_h)
                    else:
                        servos.backward(channels=tuple([SERVO_H]), speed=speed_h)
            else:
                pid_x.reset()  # Zera o acúmulo da integral enquanto pausado

            # Telemetria na Tela
            fps = 1.0 / (time.time() - start_time)
            temp_cpu = get_cpu_temp()
            info_text = f"FPS: {fps:.1f} | Temp: {temp_cpu:.1f}C | ErrX: {norm_error_x:.2f} | PID_X: {u_x:.2f}"
            opencv.putText(
                frame,
                info_text,
                (20, 30),
                opencv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

            opencv.imshow("Teste - YOLOv8 ONNX (Pi5)", frame)

            key = opencv.waitKey(10) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("p"):
                servos.stop(channels=tuple([SERVO_V, SERVO_H]))
                pause = True
            elif key == ord("c"):
                pause = False

    camera.cleanup()
    opencv.destroyAllWindows()