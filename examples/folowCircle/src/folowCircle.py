from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
import cv2 as openCv
from pathlib import Path
from .decision import voting, inInterval
from .error_signal import nomalize, activation_function, smoothed_error
import numpy


def folowCircle():
    HEIGHT = 640 # Altura da imagem 
    WIDTH = 640 # Largura da imagem
    THRES_RED = 350_000 # Limite de proximidade para detectar a bola com base no raio máximo (pi * r²): r = 320
    CIRCLE_THRES = 40  # tolerância para considerar mesma circuferencia
    NO_DET_LIMIT = 10  # número máximo de frames sem detecção
    #R_SPEED = 60 # Velocidade de investida para seguir a bola
    #X_SPEED = 40 # Velocidade para controle direcional no eixo X
    SEARCH_SPEED = 70
    have_detect = False  # Verifica se já teve alguma detecção
    circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
    counterHistory = 0 # Quantidade de frames acumulados
    noDetCounter = 0 # contador para quantidade de frames sem detecção
    x_center = WIDTH // 2 # Centro do frame no eixo x
    max_r =  min(WIDTH, HEIGHT) // 2 # Raio máximo
    pause = True # Varial para ativar os motores
    last_error = None
    speed_x = 0
    
    # Carrega configurações
    config = Config(Path(__file__).parent / "config.yaml")
    
    # Carrega configuração de câmera
    #camera_configs = config.get("camera")
    
    # Inicia câmera
    picam = Camera(HEIGHT, WIDTH) 
    picam.start()
    
    # Configuração da câmera
    #picam.set_saturation(camera_configs["saturation"])
    #picam.set_brightness(camera_configs["brigh"])
    #picam.set_contrast(camera_configs["contrast"])

    motor_config = config.get("gpio")["motor"]
    
    robot = Robot(
        left=motor_config["right"], 
        right=motor_config["left"],
        calibration=Calibration(
            right=motor_config["calibration"]["right"],
            left=motor_config["calibration"]["left"]
        )
    )
    
    # Configura controlador PID para p eixo x
    pid_x = PID(
        kp=0.2,  # constante de normalização para a velociade de controle x
        ki=0.4, 
        kd=0.4
    )
    
    # Configura controlador PID para o tamanho do raio 
    pid_r = PID(
        kp=0.2,
        ki=0.4,
        kd=0.4
    )
    
    # Loop principal de movimento
    while True:
        frame = picam.get_frame() # carrega frame
        
        mask = ProcessingImage.color_dual_segmentation(frame) # Aplica segmentação
        hough, _ = VisionModule.houghCircleDetect(mask) # Detecção via houghTransform
        contour =  VisionModule.circleCannyDetect(mask)  # Detecção, por meio das bordas e circularidade
        
        # Transforma em numpy array
        hough = (numpy.array(hough) if hough is not None else None)
        contour = (numpy.array(contour) if contour is not None else None) 

        # escolhe a melhor detecção entre hough e canny
        if hough is not None and contour is not None:
            det = voting(
                hough, 
                contour
            )    
        elif hough is not None:
            det = hough
        else:
            det = contour

        # Caso detecte um circulo
        if det is not None:
            noDetCounter = 0  # reset contador de frames sem detecção
            have_detect = True # Passa para true, pois teve uma detecção
            
            # Verifica a diferença na posição do circulo atual com os alteriores
            if circleHistory is None or not inInterval(det, circleHistory, CIRCLE_THRES):
                circleHistory = det.copy() # Pega os dados do circulo
                counterHistory = 1
                
            else: # Incrementa a media acumulativa
                circleHistory = (det + circleHistory) // 2 # Talves dê problema, mas vamo na fé
                counterHistory += 1

        else: # Sem detecção de circulos
            noDetCounter += 1
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None
                counterHistory = 0

        txt = "Nenhum circulo detectado"
        
        if circleHistory is not None:
            x, y, r = circleHistory
            error_x = x - x_center # Velocidade para centralizar a bola
            error_r = r - max_r # Velocidade para correr atrás da bola
            
            if r >= 100:
                right = 0
                left = 0
                speed_x = 0
                error_x = 0 
                
            elif error_x != 0:
                error_x = activation_function(error_x, thers=CIRCLE_THRES)

                if last_error is None:
                    last_error = error_x
                else:
                    error_x = int(smoothed_error(error_x, last_error, alph=0.3))
                    last_error = error_x

                if error_x != 0:
                    error_x = nomalize(error_x, (WIDTH / 2))
                    
                    # Controle dos motores caso tenha um cículo
                    speed_x =  pid_x.computer(abs(error_x)) # Usando só o controle proporcional
                    
                    nomalize(speed_x, 100)
                
                else: 
                    speed_x = 0
            
            # Configuração do texto do frame
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 0, 255), -1)
            txt = f"Error em X = {error_x:.2f} | Sinal PDI: {speed_x:.2f} | ({x},{y})"
            
        openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        openCv.imshow("Deteccao Final", frame)
        openCv.imshow("Mascara", mask)

        key = openCv.waitKey(10) & 0xFF 

        if key == ord('q'):
            break
        
        elif key == ord("p"):
            pause = True
        
        elif key == ord("c"):
            pause = False

        # calcula a quantidade de vermelho na cena
        red_area = openCv.countNonZero(mask)

        # Se não tiver em modo pausa pode acionar as operações de movimento
        if not pause:
            # Sem detectar circulos
            if circleHistory is None:
                print(f"Area vermelha: {red_area}")      
                            
                if not have_detect: # Não detectou nenhum circulo ainda
                    robot.turn_right(SEARCH_SPEED)
                    
                elif red_area >= THRES_RED: # Verifica proximidade da bola com base na quantidade de vermelho
                    robot.stop()
                    
                else: # Procura com base na ultima detecção
                    if error_x > 0:
                        robot.turn_left(SEARCH_SPEED) # Procura virando para a direita
                    else:
                        robot.turn_right(SEARCH_SPEED) # Procura virando para a direita
                        
            else: # Segue circulo                    
                    print(f"Velocidade:\nL - {left}\nR - {right}")
                    robot.move(speed_left=left, speed_right=right)
        
        else:
            robot.stop()
            
    robot.cleanup()
    picam.cleanup()
    openCv.destroyAllWindows()