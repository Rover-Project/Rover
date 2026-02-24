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
    THRES_RED = 350_000 # Limite de proximidade para detectar a bola com base no raio máximo (pi * r²): r = 320
    CIRCLE_THRES = 40  # tolerância para considerar mesma circuferencia
    NO_DET_LIMIT = 10  # número máximo de frames sem detecção
    R_SPEED = 60 # Velocidade de investida para seguir a bola
    X_SPEED = 40 # Velocidade para controle direcional no eixo X
    SEARCH_SPEED = 70
    have_detect = False  # Verifica se já teve alguma detecção
    circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
    counterHistory = 0 # Quantidade de frames acumulados
    noDetCounter = 0 # contador para quantidade de frames sem detecção
    x_center = WIDTH // 2 # Centro do frame no eixo x
    max_r =  min(WIDTH, HEIGHT) // 2 # Raio máximo
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
    
    robot = Robot(
        left=motor_config["left"], 
        right=motor_config["right"],
        calibration=Calibration(
            right=motor_config["calibration"]["right"],
            left=motor_config["calibration"]["left"]
        )
    )
    
    # Configura controlador PID para p eixo x
    pid_x = PID(
        kp=(X_SPEED / x_center),  # constante de normalização para a velociade de controle x
        ki=1, 
        kd=1
    )
    
    # Configura controlador PID para o tamanho do raio 
    pid_r = PID(
        kp=(R_SPEED / max_r),
        ki=1,
        kd=1
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
            
            # Controle dos motores caso tenha um cículo
            speed_x =  pid_x.controller_P(abs(error_x)) # Usando só o controle proporcional
            speed_r = pid_r.controller_P(abs(error_r))
            
            right = (speed_x + speed_r if error_x < 0 else speed_r)
            left = (speed_x + speed_r if error_x > 0 else speed_r)
            
            # Configuração do texto do frame
            openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
            openCv.circle(frame, (x, y), 3, (0, 0, 255), -1)
            txt = f"Error em X = {error_x} | Error em R = {error_r} | left = {left} | right = {right}"
            
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