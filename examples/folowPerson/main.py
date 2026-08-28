from pathlib import Path
import time
import cv2 as opencv
import numpy
import onnxruntime as onnx

from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.robot import Robot
from roverlib.utils.config_manager import Config

# configurção yolov8
MODEL_PATH = Path(__file__).parent / "models" / "yolov8n.onnx"
IMAGE_SIZE = 320      # tamanho da imagem do modelo
CONF_THRESHOLD = 0.4  # Limiar de confiança para considerar a detecção

HEIGHT = 640
WIDTH = 640
CLASS_INTEREST = {0: "Pessoa"}

DEADZONE_X = 25       # Tolerância de erro no eixo X (px)
DEADZONE_H = 20       # Tolerância de erro na altura da bounding box (px)
SMOOTH_ALFA = 0.3     # Coeficiente do filtro passa-baixas

TARGET_BOX_HEIGHT = 280  # Altura desejada da caixa (pessoa próxima/alvo)
MAX_VALUE_ROT = 60       # Limite de velocidade para rotação
MAX_VALUE_DIST = 50      # Limite de velocidade para avanço/recuo
SEARCH_SPEED = 40        # Velocidade para rotacionar quando perder o alvo
NO_DET_LIMIT = 15        # Limite de frames sem detecção para resetar PID

def get_cpu_temp():
    """Lê a temperatura atual da CPU na Raspberry Pi 5."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0

def smooth_signal(current, last, alpha=0.3):
    """Filtro passa-baixas exponencial."""
    return alpha * current + (1 - alpha) * last

if __name__ == "__main__":
    # 1. Carrega o modelo ONNX na CPU
    providers = ["CPUExecutionProvider"]
    model_session = onnx.InferenceSession(MODEL_PATH, providers=providers)
    input_name = model_session.get_inputs()[0].name

    # 2. Inicialização dos Motores DC via Configuração
    config = Config(Path(__file__).parent / "config.yaml")
    motor_config = config.get("gpio")["motor"]

    robot = Robot(
        left=motor_config["right"],
        right=motor_config["left"],
        calibration=Calibration(
            right=motor_config["calibration"]["right"],
            left=motor_config["calibration"]["left"],
        ),
    )
    
    # PID Rotação (Gira o robô para centralizar a pessoa no eixo X)
    pid_x = PID(kp=25.0, ki=15.0, kd=10.0, max_I=60.0, max_dt=0.5)
    
    # PID Distância (Maneja avanço/recuo baseado na altura da pessoa na imagem)
    pid_r = PID(kp=20.0, ki=10.0, kd=8.0, max_I=50.0, max_dt=0.5)

    # Inicializa Câmera
    camera = AfCamera(height=HEIGHT, width=WIDTH)
    camera.start()

    # Variáveis de Estado
    last_error_x = None
    last_error_h = None
    no_det_counter = 0
    pause = True

    print("Sistema pronto. Pressione 'c' na janela para INICIAR e 'p' para PAUSAR.")

    try:
        while True:
            frame = camera.get_frame()

            if frame is not None:
                start_time = time.time()
                HEIGHT, WIDTH = frame.shape[:2]
                x_center_img = WIDTH // 2

                # Pré-processamento ONNX 
                img = opencv.resize(frame, (IMAGE_SIZE, IMAGE_SIZE), opencv.INTER_CUBIC)
                input_tensor = img.astype(numpy.float32) / 255.0
                input_tensor = numpy.transpose(input_tensor, (2, 0, 1))
                input_tensor = numpy.expand_dims(input_tensor, axis=0)

                # Inferência YOLOv8 
                results = model_session.run(None, {input_name: input_tensor})[0]
                predictions = numpy.squeeze(results).T

                boxes = []
                confidences = []
                x_factor = WIDTH / IMAGE_SIZE
                y_factor = HEIGHT / IMAGE_SIZE

                # Extração de Bounding Boxes 
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

                # Non-Maximum Suppression (NMS)
                indices = opencv.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, 0.45)

                detection_found = False
                c_x, target_h = 0, 0

                # Agrupamento / Seleção do Alvo
                if len(indices) > 0:
                    detection_found = True
                    no_det_counter = 0

                    array_x, array_y, array_w, array_h = [], [], [], []
                    for detection in indices.flatten():
                        array_x.append(min(boxes[detection][0], WIDTH))
                        array_y.append(min(boxes[detection][1], HEIGHT))
                        array_w.append(min(boxes[detection][2], WIDTH))
                        array_h.append(min(boxes[detection][3], HEIGHT))

                    # Delimita uma bounding box envolvente para todas as pessoas
                    min_x, min_y = min(array_x), min(array_y)
                    max_x = min(max(array_w) + max(array_x), WIDTH)
                    max_y = min(max(array_h) + max(array_y), HEIGHT)

                    w = max_x - min_x
                    target_h = max_y - min_y
                    c_x = min_x + (w // 2)
                    c_y = min_y + (target_h // 2)

                    # Desenho na tela
                    opencv.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                    opencv.circle(frame, (c_x, c_y), 5, (0, 0, 255), -1)

                else:
                    no_det_counter += 1

                # Lógica de Controle PID dos Motores
                if detection_found:
                    # Erro X (Alinhamento): diferença até o centro da imagem [-WIDTH/2, WIDTH/2]
                    raw_error_x = float(c_x - x_center_img)
                    
                    # Erro H (Distância): quanto menor a caixa, maior o erro positivo (precisa avançar)
                    raw_error_h = float(TARGET_BOX_HEIGHT - target_h)

                    # Deadzones
                    if abs(raw_error_x) < DEADZONE_X:
                        raw_error_x = 0.0
                    if abs(raw_error_h) < DEADZONE_H:
                        raw_error_h = 0.0

                    # Filtro Passa-Baixas para suavização
                    smoothed_x = raw_error_x if last_error_x is None else smooth_signal(raw_error_x, last_error_x, SMOOTH_ALFA)
                    smoothed_h = raw_error_h if last_error_h is None else smooth_signal(raw_error_h, last_error_h, SMOOTH_ALFA)

                    last_error_x = smoothed_x
                    last_error_h = smoothed_h

                    # Normalização dos erros para o intervalo [-1.0, 1.0]
                    norm_error_x = smoothed_x / (WIDTH / 2.0)
                    norm_error_h = smoothed_h / float(TARGET_BOX_HEIGHT)

                    # Saída dos PIDs
                    u_rot = pid_x.computer(norm_error_x)
                    u_dist = pid_r.computer(norm_error_h)

                    # Clamping das velocidades para limites do robô
                    u_rot = numpy.clip(u_rot, -MAX_VALUE_ROT, MAX_VALUE_ROT)
                    u_dist = numpy.clip(u_dist, -MAX_VALUE_DIST, MAX_VALUE_DIST)

                    # Cinemática Diferencial
                    # u_rot positivo: alvo está à direita, gira robô para a direita
                    left_speed = u_dist + u_rot
                    right_speed = u_dist - u_rot

                else:
                    # Perdeu o alvo por muitos frames, reseta variáveis
                    if no_det_counter >= NO_DET_LIMIT:
                        pid_x.reset()
                        pid_r.reset()
                        last_error_h = None

                # Ativação dos motores
                if not pause:
                    if detection_found:
                        robot.move(speed_left=left_speed, speed_right=right_speed)
                    else:
                        # Varredura/Busca caso tenha perdido o alvo recentemente
                        if last_error_x is not None and last_error_x > 0:
                            robot.turn_right(SEARCH_SPEED)
                        else:
                            robot.turn_left(SEARCH_SPEED)
                else:
                    robot.stop()

                fps = 1.0 / (time.time() - start_time)
                temp_cpu = get_cpu_temp()
                info_text = f"FPS: {fps:.1f} | Temp: {temp_cpu:.1f}C |"
                opencv.putText(frame, info_text, (10, 30), opencv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                opencv.imshow("YOLOv8 Motor Control - Pi5", frame)

                key = opencv.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("p"):
                    pause = True
                    robot.stop()
                elif key == ord("c"):
                    pause = False

    finally:
        robot.stop()
        robot.cleanup()
        camera.cleanup()
        opencv.destroyAllWindows()