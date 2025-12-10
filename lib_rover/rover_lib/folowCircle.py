from modules.movement.robot import Robot
from utils.config_manager import Config
import time
from circleDetect import *
import cv2 as openCv

def cameraStart(h=640, w=640, analogic=1.5, exposure = 30000, lighConfig=False):
    picam = Picamera2()
    config = picam.create_preview_configuration(
        main={
            "format": "RGB888", 
            "size": (HEIGHT, WIDTH)
            }
        )
    
    #  Configuração de iluminação
    if lighConfig:
        picam.set_controls(
            {
            "AnalogueGain": 1.5,   # controla amplificação do sensor, analogic < 1 = mais escuro
            "ExposureTime": 30000, # em microssegundos, menor = mais escuro
            }
        )
    picam.configure(config)
    picam.start()
    
    return picam
    
if __name__ == "__main__":
    HEIGHT = 640 # Altura da imagem 
    WIDTH = 640 # Largura da imagem
    SPEED = 100  # Velocidade de rotação
    CENTER_THRES = 100 # Limiar de tolerencia para o centro
    RED_THRES_LOW = 200000 # Limite inferior para a detecção de vermelho
    RED_THRES_UPPER = 400000 # Limite superior para a detecção de vermelho
    CIRCLE_THRES = 40 # Limiar para considerar uma dada bola a mesma 
    
    last_circle = None  # guarda o ultimo circulo detectado

    picam = cameraStart(HEIGHT, WIDTH) # Inicia a camera 

    circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
    counterHistory = 0 # Quantidade de frames acumulados
    LIMIAR = 40  # tolerância para considerar mesma circuferencia
    NO_DET_LIMIT = 10  # número máximo de frames sem detecção
    noDetCounter = 0 # contador para quantidade de frames sem detecção

    # Carrega configuração da gpio
    pins_motors = Config.get("gpio")
    letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    # Inicia motores
    robot = Robot(left=letf, right=right)

    # Centro do frame no eixo x
    x_center = WIDTH // 2

    # Loop principal de movimento
    while True:
        frame = picam.capture_array() # carrega frame
        mask, _, _ = colorDualSegmentation(frame) # Aplica segmentação
        hough, _ = houghDetect(mask) # Detecção via houghTransform
        contorno = circleCannyDetect(mask) # Detecção, por meio das bordas e circularidade

        # escolhe a melhor detecção entre hough e canny
        if hough is not None and contorno is not None:
            det = circleVoting(hough, contorno)
        elif hough is not None:
            det = hough
        elif contorno is not None:
            det = contorno
        else:
            det = None

        if det is not None:
            noDetCounter = 0  # reset contador de frames sem detecção

            # Verifica a discrepancia na posição do circulo atual com os alteriores
            if circleHistory is None or not inInterval(det, circleHistory, LIMIAR):
                circleHistory = list(det) # Pega os dados do circulo
                counterHistory = 1
            else: # Incrementa a media acumulativa
                circleHistory[0] += det[0]
                circleHistory[1] += det[1]
                circleHistory[2] += det[2]
                counterHistory += 1
                
            last_circle = circleHistory # captura o ultimo ciculo

        else:
            noDetCounter += 1
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None
                counterHistory = 0

        txt = "Nenhum circulo detectado"
        if circleHistory and counterHistory > 0:
            x = circleHistory[0] // counterHistory
            y = circleHistory[1] // counterHistory
            r = circleHistory[2] // counterHistory
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
            txt = f"X={x}  Y={y}  R={r}"

        openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        openCv.imshow("Deteccao Final", frame)
        openCv.imshow("Mascara", mask)

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

        # calcula a quantidade de vermelho na cena
        red_area = openCv.countNonZero(mask)

        if circleHistory is None:
            print(f"Area vermelha: {red_area}")
            if red_area >= RED_THRES_LOW and RED_THRES_UPPER > red_area: # Chegou perto o suficiente da bola
                robot.stop()
            elif last_circle:
                last_x, last_y, last_r = last_circle
                if last_x > WIDTH // 2:
                    robot.move(60, -60)  # gira para direita
                else:
                    robot.move(-60, 60)  # gira para esquerda
            else:
                print("Nenhum circulo foi detectado")
                robot.move(-60, 60)  # rotaciona procurando um círculo

        else:
            x, y, r = circleHistory
            if x > x_center + CENTER_THRES:
                robot.move(60, -60)
            elif x < x_center - CENTER_THRES:
                robot.move(-60, 60)
            else:
                robot.move(70, 100)

        time.sleep(0.1)

    picam.stop()
    openCv.destroyAllWindows()