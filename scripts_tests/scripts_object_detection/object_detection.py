# Esse script detecta e classifica objetos a partir do TensorFlowLite Interpreter.
# Carrega, o classifier, captura um frame, faz o seu pré-processamento, realiza a detecção
# propriamente dita, pós-processa as informações, desenha elas no frame e exibe tudo.

from picamera2 import PiCamera2
import tflite_runtime.interpreter as tflite
import numpy as np
import cv2
import sys
import os

# Constantes da camera (usar para outras resoluções que não são a do modelo)
# width = 640
# height = 480 

# Variáveis de caminho
MODEL_NAME = 'ssd_mobilenet_v2_320x320_tf2_20200714.tflite'
LABELS_FILE = 'labelmap.txt'

# Lê o caminho do diretório atual
CWD_PATH = os.getcwd()

# Junta os caminhos 
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELS_FILE)

# Carrega o label map
with open(PATH_TO_LABELS, 'r') as arquivo:
    labels = [line.strip() for line in arquivo.readlines()]
category_index = {i: {'id': i, 'name': label} for i, label in enumerate(labels, 1)}

# Carrega o tflite interpreter
interpreter = tflite.Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()
    
# Obtem os detalhes o input e output
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Obtem a resolução que o modelo espera
height_model = input_details[0]['shape'][1]
width_model = input_details[0]['shape'][2]

# Inicio do calc do framerate
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Inicializando a câmera
picam2 = PiCamera2()
cfg = picam2.create_video_configuration (main={"size": (width_model, height_model)}) # Config de vídeo
picam2.configure(cfg)
picam2.start()

while True:

    # Retorna o números de ciclos de clock para medição do desempenho
    t1 = cv2.getTickCount()

    # Imagem de entrada em width_model x height_model
    frame = picam2.capture_array() 
    # Seta o frame como write. Em alguns casos, ele pode vir como apenas read
    frame.setflags(write=1)

    # ----- PRÉ-PROCESSAMENTO -----

    # Redimensionamento do frame
    # Desnecessário dependendo da configuração inicial da câmera, mas pode ser usado para resoluções maiores
    frame_resized = cv2.resize(frame, (width_model, height_model))

    # Expanção das dimenções (Essêncial para melhor análise do modelo)
    input_data = np.expand_dims(frame_resized,axis=0).astype(np.uint8)
    
    # setar tensor de entrada
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # ----- INFERÊNCIA -----
    interpreter.invoke()

    # Obtenção dos resultados
    boxes = interpreter.get_tensor(output_details[0]['index'])
    classes = interpreter.get_tensor(output_details[1]['index'])
    scores = interpreter.get_tensor(output_details[2]['index'])
    num = interpreter.get_tensor(output_details[3]['index'])
    
    # ----- PÓS-PROCESSAMENTO -----
    # Gera o frame como BGR (necessário para o openCV)
    # Pode-se usar o frame_resized ou o original.
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Exibição dos resultados
    # Obtenha os resultados da inferência e "squeeze" (squeeze reduz o array para rank 3)
    boxes = np.squeeze(boxes)
    classes = np.squeeze(classes).astype(np.int32)
    scores = np.squeeze(scores)

    # ----- EXIBIÇÃO -----
    # Itera sobre todas as detecções
    for i in range(int(num)):
        score = scores[i]
        if score > 0.40: # Limite minimo de confiança na inferência
            # Obtenção das coordenadas
            # As coordenadas são normalizadas (de 0 até 1)
            # Sendo 0, canto superior esquerdo e 1, canto inferior direito
            ymin = int(boxes[i][0] * height_model)  
            xmin = int(boxes[i][1] * width_model)
            ymax = int(boxes[i][2] * height_model)
            xmax = int(boxes[i][3] * width_model)

            # Obter rótulo e cor
            class_id = classes[i]
            label = category_index[class_id]['name']

            # Cor BGR 
            color = (0, 0, 255) # Retângulos vermelhos

            # Desenhando o retângulo
            # 3 é a espessura da linha
            cv2.rectangle(frame_bgr, (xmin, ymin), (xmax, ymax), color, 3)
            
            # Desenhando o rótulo e score
            label_text = '%s: %d%%' % (label, int(score*100))

            # Desenha um fundo preto para facilitar a leitura
            # Opcional mas util para possibilitar a leitura em qualquer plano de fundo
            cv2.rectangle(frame_bgr, (xmin, ymin - 15), (xmin + len(label_text)*10, ymin), color, -1)

            # Desenha o texto
            cv2.putText(frame_bgr, label_text, (xmin, ymin - 5), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    # Adiciona o framerate a tela.
    cv2.putText(frame_bgr,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)

    # Método que exibe todas as informações desenhadas no frame.
    cv2.imshow('Object detector', frame_bgr)

    # Lógica de cálculo do frame_rate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc = 1/time1

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

picam2.close()