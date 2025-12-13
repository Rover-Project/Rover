import cv2
from ultralytics import YOLO

# Carrega o modelo TFLite que você exportou no notebook
# Certifique-se de que o arquivo .tflite está na mesma pasta
model_path = r"C:\Users\gutop\Desktop\TCC - Rover\rover_lib\roverRefator\Rover\scripts_tests\scripts_object_detection\models\Esferas_V2_int8.tflite"

model = YOLO(model_path, task='detect')

# Inicializa a câmera (0 geralmente é a câmera USB ou Pi Camera via libcamera)
cap = cv2.VideoCapture(0)

# Configurações do Rover
CENTER_TOLERANCE = 50  # Zona morta no centro da imagem
FRAME_WIDTH = 640

# Função simulada de controle dos motores (Substitua pela sua lógica de GPIO)
def control_rover(action):
    print(f"Comando para o Rover: {action}")
    # Aqui você colocaria o código GPIO, ex:
    # if action == "ESQUERDA": gpio.output(PIN_LEFT, 1)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Realiza a inferência
    # imgsz=640 deve ser igual ao usado no treinamento do notebook
    results = model(frame, imgsz=640, conf=0.5, verbose=False)

    # Processa os resultados
    if results[0].boxes:
        # Pega a caixa com maior confiança (objeto vermelho mais provável)
        box = results[0].boxes[0]
        
        # Coordenadas da caixa (x1, y1, x2, y2)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        # Calcula o centro do objeto
        center_x = (x1 + x2) / 2
        image_center = FRAME_WIDTH / 2
        
        # Lógica de Navegação
        if center_x < (image_center - CENTER_TOLERANCE):
            control_rover("VIRAR ESQUERDA")
        elif center_x > (image_center + CENTER_TOLERANCE):
            control_rover("VIRAR DIREITA")
        else:
            control_rover("SEGUIR EM FRENTE")
            
        # Desenha a caixa para visualização (opcional, deixa o sistema mais lento)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, "Objeto Vermelho", (int(x1), int(y1)-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        control_rover("PARAR - Objeto não encontrado")

    # Mostra a imagem (se houver monitor conectado, caso contrário comente as linhas abaixo)
    cv2.imshow("Visao do Rover", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()