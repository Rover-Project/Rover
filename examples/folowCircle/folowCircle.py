from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.utils.config_manager import Config
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
import cv2 as openCv
from pathlib import Path
import numpy

def voting(hough: numpy.ndarray, contour: numpy.ndarray, thers_xy: int = 20, thers_r: float = 0.3) -> numpy.ndarray:
    """
    Função de votação, para os dois métodos de detectção do círculo.

    Args:
        hough (tuple[int, int, int]): x, y e r da detecção da transformada de Hough
        contorno (tuple[int, int, int]): x, y e r  da detecção do método de contornos
        thers_xy (int, optional): Limiar de diferença para as coordenadas x e y. Por padrão 20.
        thers_r (float, optional): Limiar de diferença entre os raios. Por padrão 0.3.

    Returns:
        numpy.ndarray: Retorna uma média da coordenadas caso a discordância for menos que os limiares. Caso contrário retorna o método mais confiavel. 
    """
    
    # votação
    if abs(numpy.sum(hough[:2] - contour[:2])) < thers_xy:
        if abs(hough[2] - contour[2]) < (hough[2] * thers_r):
            return (hough + contour) // 2 

    # Se a discordancia for alta, retorna o metodo mais seguro
    return contour
    
def inInterval(v1: numpy.ndarray, v2: numpy.ndarray, thers: float) -> bool:
    """
    Verifica se a diferença de dois vetores é menor que que o limiar.

    Args:
        v1 (numpy.ndarray): Primeiro array. 
        v2 (numpy.ndarray): Segundo array.
        thers (int): limiar de diferença.

    Returns:
        bool: True se a diferença for menor que o limiar.
    """
    
    if abs(numpy.sum(v1 - v2)) > thers:
        return False
    
    return True

def folowCircle():
    HEIGHT = 640 # Altura da imagem 
    WIDTH = 640 # Largura da imagem
    RED_THRES_LOW = 200000 # Limite inferior para a detecção de vermelho
    RED_THRES_UPPER = 400000 # Limite superior para a detecção de vermelho
    CIRCLE_THRES = 40  # tolerância para considerar mesma circuferencia
    NO_DET_LIMIT = 10  # número máximo de frames sem detecção
    BASE_SPEED = 60 # Velocidade base para controle
    SEARCH_SPEED = 70
    last_circle = None  # guarda o ulthimo circulo detectado
    circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
    counterHistory = 0 # Quantidade de frames acumulados
    noDetCounter = 0 # contador para quantidade de frames sem detecção
    x_center = WIDTH // 2 # Centro do frame no eixo x
    pause = True # Varial para ativar os motores
    
    # Carrega configurações
    config = Config(Path(__file__).parent / "config.yaml")
    
    # Carrega configuração de câmera
    camera_configs = config.get("camera")
    
    # Inicia câmera
    picam = Camera(HEIGHT, WIDTH) 
    picam.start()
    
    # Configuração da câmera
    picam.set_saturation(camera_configs["saturation"])
    picam.set_brightness(camera_configs["brigh"])
    picam.set_contrast(camera_configs["contrast"])

    motor_config = config.get("gpio")["motor"]

    # Configura motores
    print(motor_config["left"])
    print(motor_config["right"])
    
    robot = Robot(
        left=motor_config["left"], 
        right=motor_config["right"],
        calibration=Calibration(
            right=motor_config["calibration"]["right"],
            left=motor_config["calibration"]["left"]
        )
    )
    
    # Configura controlador PID
    pid = PID(
        kp=1, 
        ki=1, 
        kd=1
    )
    
    # Loop principal de movimento
    while True:
        frame = picam.get_frame() # carrega frame
        
        mask = ProcessingImage.color_dual_segmentation(frame) # Aplica segmentação
        hough, _ = VisionModule.houghCircleDetect(mask) # Detecção via houghTransform
        contorno = VisionModule.circleCannyDetect(mask) # Detecção, por meio das bordas e circularidade

        # escolhe a melhor detecção entre hough e canny
        if hough is not None and contorno is not None:
            det = voting(
                numpy.array(hough), 
                numpy.array(contorno)
            )
        elif hough is not None:
            det = numpy.array(hough)
        elif contorno is not None:
            det = numpy.array(contorno)
        else:
            det = None

        # Caso detecte um circulo
        if det is not None:
            noDetCounter = 0  # reset contador de frames sem detecção

            # Verifica a diferença na posição do circulo atual com os alteriores
            if circleHistory is None or not inInterval(det, circleHistory, CIRCLE_THRES):
                circleHistory = det.copy() # Pega os dados do circulo
                counterHistory = 1
                
            else: # Incrementa a media acumulativa
                circleHistory += det
                counterHistory += 1
                
            last_circle = circleHistory.copy() # captura o ultimo ciculo

        else: # Sem detecção de circulos
            noDetCounter += 1
            if noDetCounter >= NO_DET_LIMIT:
                circleHistory = None
                counterHistory = 0

        txt = "Nenhum circulo detectado"
        
        if circleHistory is not None and counterHistory > 0:
            x, y, r = (circleHistory // counterHistory)
            error_x = x - x_center 
            
            # Controle dos motores caso tenha um cículo
            speed_x =  pid.controller_P(abs(error_x)) * ((100 - BASE_SPEED) / x_center)  # Usando só o controle proporcional
            right = (speed_x + BASE_SPEED if error_x < 0 else BASE_SPEED)
            left = (speed_x + BASE_SPEED if error_x > 0 else BASE_SPEED)
            
            # Configuração do texto do frame
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 0, 255), -1)
            txt = f"Error = {error_x} | left = {left} | right = {right}"
            
        openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
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
                if error_x > 0:
                    robot.move(speed_left=SEARCH_SPEED, speed_right=0) # Procura virando para a direita
                else:
                    robot.move(speed_left=0, speed_right=SEARCH_SPEED) # Procura virando para a esquerda
                        
            else: # Segue circulo                    
                    print(f"Velocidade:\nL - {left}\nR - {right}")
                    robot.move(speed_left=left, speed_right=right)
        
        else:
            robot.stop()
            
    robot.cleanup()
    picam.cleanup()
    openCv.destroyAllWindows()