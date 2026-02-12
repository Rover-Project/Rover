from roverlib.modules.movement.robot import Robot
from roverlib.utils.config_manager import Config
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.camera.webcam import Webcam
import cv2 as openCv
import time 
from pathlib import Path

def circleVoting(hough, contorno):
    """Relaciona a detecção de dois metodos diferente"""
    
    if hough is None and contorno is None: # nada detectado
        return None

    if hough is None: # Somente um metodo detectou
        return contorno

    if contorno is None: # Somente um metodo detectou
        return hough

    x1, y1, r1 = hough
    x2, y2, r2 = contorno
    
    x1, y1, r1 = int(x1), int(y1), int(r1)
    x2, y2, r2 = int(x2), int(y2), int(r2)

    # votação:
    if abs(x1 - x2) < 20 and abs(y1 - y2) < 20:
        if abs(r1 - r2) < (r1 * 0.30):
            return ((x1 + x2)//2, (y1 + y2)//2, int((r1 + r2) / 2))

    # Se a discordancia for alta, retorna o metodo mais seguro
    return contorno
    
def inInterval(last, current, LIMIAR):
    # a e b são tuplas/listas (x, y, r)
    if current is None:
        return False
    for i in range(3):
        if abs(last[i] - current[i]) > LIMIAR:
            return False
    return True


class FolowCircle:
    
    _integral = 0
    _last_error = 0 
    _dt = 0
    
    @classmethod
    def controllerPID(cls, error:float, kp = 1.0, ki = 1.0, kd = 1.0): 
        cls._integral += error * cls._dt
        
        cp = error * kp # controle proporcional 
        ci = cls._integral * ki # controle integral
        cd = kd * (error - cls._last_error) / cls._dt # controle derivativo

        cls._last_error = error
        
        speed = cp + ci + cd
        
        return speed, -speed # motor esquerdo, mortor direito
    
    @classmethod
    def updateTime(cls):
        cls._dt = time.time() - cls._dt # Atualiza o tempo 
        
    @classmethod
    def folowCircle(cls):
        HEIGHT = 640 # Altura da imagem 
        WIDTH = 640 # Largura da imagem
        #BALANCING_ROTACION_ANTH = 6 / 10 # Balanceamento para rotação no sentido ant-horário
        RED_THRES_LOW = 200000 # Limite inferior para a detecção de vermelho
        RED_THRES_UPPER = 400000 # Limite superior para a detecção de vermelho
        CIRCLE_THRES = 40  # tolerância para considerar mesma circuferencia
        NO_DET_LIMIT = 10  # número máximo de frames sem detecção
        last_circle = None  # guarda o ulthimo circulo detectado

        try:
            picam = Camera(HEIGHT, WIDTH) # Inicia a camera 
            picam.start()
        except:
            #picam = Webcam(HEIGHT, WIDTH)
            pass 
        
        circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
        counterHistory = 0 # Quantidade de frames acumulados
        
        noDetCounter = 0 # contador para quantidade de frames sem detecção

        # Carrega configuração da gpio
        # Carrega configuração da gpio
        config = Config(Path(__file__).parent / "config.yaml")
    
        pins_motors = config.get("gpio")
        letf = (int(pins_motors["motor_esquerdo"]["in1"]), int(pins_motors["motor_esquerdo"]["in2"]))
        right = (int(pins_motors["motor_direito"]["in3"]), int(pins_motors["motor_direito"]["in4"]))
    
        # Inicia motores
        robot = Robot(left=letf, right=right)

        # Centro do frame no eixo x
        x_center = WIDTH // 2
        pause = True

        cls._integral = 0
        cls._last_error = 0
        cls._dt = time.time() # Inicializa a varial de tempo
        
        BASE_SPEED = 80
        
        # Loop principal de movimento
        while True:
            frame = picam.getFrame() # carrega frame
            
            cls.updateTime() # atualiza o tempo de captura
            
            mask = ProcessingImage.color_dual_segmentation(frame) # Aplica segmentação
            hough, _ = VisionModule.houghCircleDetect(mask) # Detecção via houghTransform
            contorno = VisionModule.circleCannyDetect(mask) # Detecção, por meio das bordas e circularidade

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
                if circleHistory is None or not inInterval(det, circleHistory, CIRCLE_THRES):
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

            key = openCv.waitKey(1) & 0xFF 

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
                if circleHistory is None:
                    print(f"Area vermelha: {red_area}")
                    if red_area >= RED_THRES_LOW and RED_THRES_UPPER > red_area: # Chegou perto o suficiente da bola
                        robot.stop()
                        
                    elif last_circle:
                        last_x, _, _ = last_circle
                        
                        left, right = FolowCircle.controllerPID(x_center - last_x)
                        
                        left = (left + BASE_SPEED if left > 0 else left - BASE_SPEED)
                        right = (right + BASE_SPEED if right > 0 else right - BASE_SPEED)
                        
                        
                        print(f"Velocidade:\nL - {left}\nR - {right}")
                        robot.move(speed_left=left, speed_right=right)
                        
                    else:
                        print("Nenhum circulo foi detectado")
                        robot.move(speed_left=BASE_SPEED, speed_right=-BASE_SPEED)  # rotaciona procurando um círculo
            else:
                robot.stop()

            time.sleep(0.1)

        robot.cleanup()
        picam.cleanup()
        openCv.destroyAllWindows()