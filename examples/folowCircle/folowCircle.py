from lib_rover.rover_lib.modules.movement.robot import Robot
from lib_rover.rover_lib.utils.config_manager import Config
from lib_rover.rover_lib.modules.processing.processing_image import ProcessingImage
from lib_rover.rover_lib.modules.vision.visionModule import VisionModule
from lib_rover.rover_lib.modules.camera.cameraModule import CameraModule
from lib_rover.rover_lib.modules.camera.webcam import Webcam
from ..circleDetect.circleDetect import circleVoting, inInterval
import cv2 as openCv
import time 

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
        SPEED = 100  # Velocidade de rotação
        BALANCING_ROTACION_H = 5 / 10 # Balanceamento para rotação no sentido horário
        BALANCING_ROTACION_ANTH = 6 / 10 # Balanceamento para rotação no sentido ant-horário
        BALANCING_MOTOR_RIGHT = 1 # Balanceamento para o motor direito 
        BALANCING_MOTOR_LEFT = 7 / 10 # Balanceamento para o motor esquerdo
        CENTER_THRES = 250 # Limiar de tolerencia para o centro
        RED_THRES_LOW = 200000 # Limite inferior para a detecção de vermelho
        RED_THRES_UPPER = 400000 # Limite superior para a detecção de vermelho
        CIRCLE_THRES = 40  # tolerância para considerar mesma circuferencia
        NO_DET_LIMIT = 10  # número máximo de frames sem detecção
        last_circle = None  # guarda o ulthimo circulo detectado

        try:
            picam = CameraModule(HEIGHT, WIDTH) # Inicia a camera 
        except:
            picam = Webcam(HEIGHT, WIDTH)

        circleHistory = None  # média acumulada, para suavizar as mudanças de posição do circulo
        counterHistory = 0 # Quantidade de frames acumulados
        
        noDetCounter = 0 # contador para quantidade de frames sem detecção

        # Carrega configuração da gpio
        pins_motors = Config.get("gpio")
        letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
        right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

        # Inicia motores
        robot = Robot(left=letf, right=right)

        # Centro do frame no eixo x
        x_center = WIDTH // 2
        pause = True

        cls._integral = 0
        cls._last_error = 0
        cls._dt = time.time() # Inicializa a varial de tempo

        # Loop principal de movimento
        while True:
            frame = picam.get_frame() # carrega frame
            
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
                        robot.move(speed_left=left, speed_right=right)
                        
                    else:
                        print("Nenhum circulo foi detectado")
                        robot.move(speed_left=-SPEED * BALANCING_ROTACION_ANTH, speed_right=SPEED * BALANCING_ROTACION_ANTH)  # rotaciona procurando um círculo

                else:
                    x, y, r = circleHistory
                    if x > x_center + CENTER_THRES:
                        robot.move(speed_left=SPEED * BALANCING_ROTACION_H, speed_right=-SPEED * BALANCING_ROTACION_H)
                    elif x < x_center - CENTER_THRES:
                        robot.move(speed_left=-SPEED * BALANCING_ROTACION_ANTH, speed_right=SPEED * BALANCING_ROTACION_ANTH)
                    else:
                        robot.move(speed_left=SPEED * BALANCING_MOTOR_LEFT,speed_right=SPEED * BALANCING_MOTOR_RIGHT)
            else:
                robot.stop()

            time.sleep(0.1)

        robot.cleanup()
        picam.cleanup()
        openCv.destroyAllWindows()