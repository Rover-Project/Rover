from pathlib import Path
import cv2 as opencv
import numpy
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.modules.movement.PID import PID
from roverlib.modules.movement.robot import Robot
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config

from .decision import inInterval, voting
from .error_signal import activation_function, normalize, smooth_signal, activation_deadzone

def folowCircle():
  HEIGHT = 640 # Altura da imagem
  WIDTH = 640  # Largura da imagem
  THRES_RED = 350_000  # Limite de proximidade para detectar a bola
  CIRCLE_THRES_X = 40  # Tolerância de variação no círculo
  RADIUS_THRES_R = 20
  NO_DET_LIMIT = 10  # Limite de frames sem detecção
  SEARCH_SPEED = 50  # Velocidade para busca da bola

  CIRCLE_THRES = 50 

  # Raio desejado para a bola 
  TARGET_RADIUS = 150
  
  # centro da imagem 
  X_CENTER = WIDTH // 2 

  # Limiares de acionamento mínimo
  MIN_PW_LEFT = 40.0
  MIN_PW_RIGHT = 30.0
  
  MAX_VALUE_ROT = 60
  MAX_VALUE_DIST = 40

  have_detect = False
  circleHistory = None # cuidado com unsignedint
  counterHistory = 0
  noDetCounter = 0
  pause = True
  last_error_x = None
  last_error_r = None

  # Carrega configurações
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

  # PID para Rotação 
  pid_x = PID(kp=20.0, ki=15.0, kd=15.0, max_I=30.0)

  # PID para Distância
  pid_r = PID(kp=40.0, ki=10, kd=10, max_I=30.0)

  # Câmera
  picam = Camera(HEIGHT, WIDTH)
  picam.start()

  while True:
    frame = picam.get_frame()
    
    if frame is not None:
      
      frame = opencv.resize(frame, (HEIGHT, WIDTH))

      mask = ProcessingImage.color_dual_segmentation(frame)
      hough, _ = VisionModule.houghCircleDetect(mask)
      contour = VisionModule.circleCannyDetect(mask)

      hough = numpy.array(hough) if hough is not None else None
      contour = numpy.array(contour) if contour is not None else None

      if hough is not None and contour is not None:
        det = voting(hough, contour)
        
      elif hough is not None:
        det = hough
        
      else:
        det = contour

      if det is not None:
        noDetCounter = 0
        have_detect = True

        if circleHistory is None or not inInterval(
            det, circleHistory, CIRCLE_THRES
        ):
          circleHistory = det.copy()
          counterHistory = 1
        else:
          circleHistory = (det + circleHistory) // 2
          counterHistory += 1
      else:
        noDetCounter += 1
        if noDetCounter >= NO_DET_LIMIT:
          circleHistory = None
          counterHistory = 0
          
          pid_x.reset()
          pid_r.reset()
          last_error_x = None

      txt = "Nenhum circulo detectado"
      left_speed = 0.0
      right_speed = 0.0

      if circleHistory is not None:
        x, y, r = circleHistory
              
        error_x = int(X_CENTER) - int(x) # calculo do erro no eixo X, erro_x pertence [-X_CENTER, X_CENTER]
        
        error_r = -(int(r) - int(TARGET_RADIUS)) # calcula do erro no em relação a distância
        
        # função de ativação para o erro no eixo X
        raw_error_x = activation_function(error_x, deadzone=CIRCLE_THRES_X) 
        raw_error_r = activation_function(error_r, deadzone=RADIUS_THRES_R)  
          
        # suaviza o erro com filtro passas baixas
        if last_error_x is None:
          smoothed_x = raw_error_x
        else:
          smoothed_x = smooth_signal(raw_error_x, last_error_x, alph=0.3) 
          
        # suaviza o erro com filtro passas baixas
        if last_error_r is None:
          smoothed_r = raw_error_r
        else:
          smoothed_r = smooth_signal(raw_error_r, last_error_r, alph=0.3) 
      
        last_error_x = smoothed_x
        last_error_r = smoothed_r

        # normaliza o erro para o intervalo [-1, 1]
        norm_error_x = normalize(error=smoothed_x, radius=WIDTH//2)
        norm_error_r = normalize(error=smoothed_r, radius=240)
        
        # cácula os valores PID para x e r
        u_rot = min(pid_x.computer(norm_error_x), MAX_VALUE_ROT)
        u_dist = min(pid_r.computer(norm_error_r), MAX_VALUE_DIST)
      
        # velocidades diferenciais 
        raw_left = u_dist - u_rot
        raw_right = u_dist + u_rot
        
        right_speed = -raw_right
        left_speed = raw_left

        # Renderização visual no OpenCV
        opencv.circle(frame, (x, y), r, (0, 255, 0), 3)
        opencv.circle(frame, (x, y), 3, (0, 0, 255), -1)
        txt = f"PID_R: {u_dist:.2f} | right: {right_speed:.2f} | left: {left_speed:.2f}"

      opencv.putText(
          frame, txt, (10, 35), opencv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
      )
      opencv.imshow("Deteccao Final", frame)
      opencv.imshow("Mascara", mask)

      key = opencv.waitKey(10) & 0xFF
      if key == ord("q"):
        break
      elif key == ord("p"):
        pause = True
      elif key == ord("c"):
        pause = False

      red_area = opencv.countNonZero(mask)

      # Controle dos Atuadores
      if not pause:
        if circleHistory is None:
          if not have_detect:
            robot.turn_right(SEARCH_SPEED)
            print(SEARCH_SPEED)
          elif red_area >= THRES_RED:
            robot.stop()
          else:
            if last_error_x is not None and last_error_x < 0:
              robot.turn_left(SEARCH_SPEED)
              print(SEARCH_SPEED)
            else:
              robot.turn_right(SEARCH_SPEED)
              print(SEARCH_SPEED)
        else:
          robot.move(speed_left=left_speed, speed_right=right_speed)
      else:
        robot.stop()

  robot.cleanup()
  picam.cleanup()
  opencv.destroyAllWindows()