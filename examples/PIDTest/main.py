from pathlib import Path
import time
import cv2 as opencv
import numpy
import onnxruntime as onnx
from roverlib.modules.movement.PID import PID
import matplotlib.pyplot as plt

# Configurações do Modelo e Câmera
MODEL_PATH = Path(__file__).parent / "models" / "yolov8n.onnx"
IMAGE_SIZE = 320  # Resolução de entrada da YOLO
CONF_THRESHOLD = 0.4  # Limiar de confiança para detecção
HEIGHT = 640
WIDTH = 640
DEADZONE = 25
SMOOTH_ALFA = 0.3
CLASS_INTEREST = {0: "Pessoa"}

if __name__ == "__main__":
    providers = ["CPUExecutionProvider"]  # Força execução na CPU

    model_session = onnx.InferenceSession(MODEL_PATH, providers=providers)
    input_name = model_session.get_inputs()[0].name

    # Inicia câmera 
    camera = opencv.VideoCapture(0)

    # 1. Instancia os controladores PID (Ajuste kp, ki, kd conforme seu sistema)
    pid_x = PID(kp=0.005, ki=0.001, kd=0.0005, max_I=1.0)
    pid_y = PID(kp=0.005, ki=0.001, kd=0.0005, max_I=1.0)

    # 2. Listas para armazenar o histórico de dados
    time_history = []
    error_x_history, error_y_history = [], []
    pid_x_history, pid_y_history = [], []
    
    start_script_time = time.time()

    # 3. Configuração do Plot em Tempo Real via Matplotlib
    plt.ion()  # Ativa modo interativo do matplotlib
    fig, (ax_err, ax_pid) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    fig.suptitle("Desempenho do Controlador PID")

    # Linhas do gráfico de Erro
    (line_err_x,) = ax_err.plot([], [], "r-", label="Erro X (px)")
    (line_err_y,) = ax_err.plot([], [], "b-", label="Erro Y (px)")
    ax_err.set_ylabel("Erro (Pixels)")
    ax_err.grid(True)
    ax_err.legend(loc="upper right")

    # Linhas do gráfico de Saída do PID
    (line_pid_x,) = ax_pid.plot([], [], "r--", label="Saída PID X")
    (line_pid_y,) = ax_pid.plot([], [], "b--", label="Saída PID Y")
    ax_pid.set_xlabel("Tempo (s)")
    ax_pid.set_ylabel("Sinal de Controle")
    ax_pid.grid(True)
    ax_pid.legend(loc="upper right")

    # Controle de frequência de atualização do gráfico
    last_plot_update = time.time()
    plot_interval = 0.1  # Atualiza o gráfico a cada 100ms
    last_smoothed_error_x = None
    last_smoothed_error_y = None

    while True:
        _, frame = camera.read()

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

            # processamento de boxes
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

            # Cálculo dos Erros nos eixos X e Y
            raw_error_x = c_x - (WIDTH // 2)
            raw_error_y = c_y - (HEIGHT // 2)
            
            # aplica um filtro de passas baixas para suavizar o error x
            if last_smoothed_error_x is None:
                smoothed_error_x = float(raw_error_x)
            else:    
                smoothed_error_x = SMOOTH_ALFA * raw_error_x + (1 - SMOOTH_ALFA) * last_smoothed_error_x 
            
            last_smoothed_error_x = smoothed_error_x # atualiza o ultimo erro suavizado
                
            # aplica um filtro de passas baixas para suavizar o error y
            if last_smoothed_error_y is None:
                smoothed_error_y = float(raw_error_y)
            else :    
                smoothed_error_y = SMOOTH_ALFA * error_y + (1 - SMOOTH_ALFA) * last_smoothed_error_y 
            
            last_smoothed_error_y = smoothed_error_y # atualiza o ultimo erro suavizado
            
            # Ignora erros menores que DEADZONE
            error_x = 0.0 if  numpy.abs(smoothed_error_x) < DEADZONE else smoothed_error_x
            error_y = 0.0 if numpy.abs(smoothed_error_y) < DEADZONE else smoothed_error_y
            
            # normaliza os erros pro intervalo [-1, 1]
            error_x = error_x / (WIDTH / 2) 
            error_y = error_y / (HEIGHT / 2)

            u_x = pid_x.computer(error_x)
            u_y = pid_y.computer(error_y)

            # Armazena histórico para os plots
            current_elapsed_time = time.time() - start_script_time
            time_history.append(current_elapsed_time)
            error_x_history.append(error_x)
            error_y_history.append(error_y)
            pid_x_history.append(u_x)
            pid_y_history.append(u_y)

            # Atualização periódica do gráfico
            if time.time() - last_plot_update > plot_interval:
                last_plot_update = time.time()

                # Atualiza dados das linhas
                line_err_x.set_data(time_history, error_x_history)
                line_err_y.set_data(time_history, error_y_history)
                line_pid_x.set_data(time_history, pid_x_history)
                line_pid_y.set_data(time_history, pid_y_history)

                # Reajusta os eixos automaticamente
                for ax in (ax_err, ax_pid):
                    ax.relim()
                    ax.autoscale_view()

                fig.canvas.draw()
                fig.canvas.flush_events()

            # Cálculo de FPS
            fps = 1.0 / (time.time() - start_time)
            
            info_text = f"FPS: {fps:.1f} | Err: ({error_x}, {error_y}) | PID: ({u_x:.2f}, {u_y:.2f})"
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

            key = opencv.waitKey(10) & 0xFF
            if key == ord("q"):
                break
            
    camera.release()
    opencv.destroyAllWindows()

    # Desativa modo interativo para manter o gráfico estático final ao fechar a câmera
    plt.ioff()
    plt.show()