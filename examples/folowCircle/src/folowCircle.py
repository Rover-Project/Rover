from pathlib import Path
import cv2 as openCv
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
  HEIGHT = 640  # Altura da imagem
  WIDTH = 640  # Largura da imagem
  THRES_RED = 350_000  # Limite de proximidade para detectar a bola
  CIRCLE_THRES = 40  # Tolerância de variação no círculo
  NO_DET_LIMIT = 10  # Limite de frames sem detecção
  SEARCH_SPEED = 60  # Velocidade para busca da bola

  # Raio desejado para a bola 
  TARGET_RADIUS = 60.0

  # Limiares de acionamento mínimo
  MIN_PW_LEFT = 40.0
  MIN_PW_RIGHT = 30.0

  have_detect = False
  circleHistory = None
  counterHistory = 0
  noDetCounter = 0
  x_center = WIDTH // 2  # Centro do frame no eixo X
  pause = True
  last_error_x = None

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
  pid_x = PID(kp=35.0, ki=0.5, kd=2.0, max_I=20.0)

  # PID para Distância
  pid_r = PID(kp=1.5, ki=0.05, kd=0.2, max_I=30.0)

  # Câmera
  picam = Camera(HEIGHT, WIDTH)
  picam.start()

  while True:
    frame = picam.get_frame()

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

      # Error no eixo X
      raw_error_x = x_center - x 
      raw_error_x = activation_function(raw_error_x, min_deadzone=CIRCLE_THRES)

      if last_error_x is None:
        smoothed_x = raw_error_x
      else:
        smoothed_x = smooth_signal(raw_error_x, last_error_x, alph=0.3)
        
      last_error_x = smoothed_x

      norm_error_x = normalize(smoothed_x, (WIDTH / 2))
      u_rot = pid_x.computer(norm_error_x)
      
      error_r = TARGET_RADIUS - r
      u_dist = pid_r.computer(error_r)
     
      raw_left = u_dist - u_rot
      raw_right = u_dist + u_rot

      left_speed = activation_deadzone(raw_left, MIN_PW_LEFT)
      right_speed = activation_deadzone(raw_right, MIN_PW_RIGHT)

      # Renderização visual no OpenCV
      openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
      openCv.circle(frame, (x, y), 3, (0, 0, 255), -1)
      txt = f"ErrX: {raw_error_x:.2f} | ErrR: {error_r:.1f} | L: {left_speed:.0f} R: {right_speed:.0f}"

    openCv.putText(
        frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
    )
    openCv.imshow("Deteccao Final", frame)
    openCv.imshow("Mascara", mask)

    key = openCv.waitKey(10) & 0xFF
    if key == ord("q"):
      break
    elif key == ord("p"):
      pause = True
    elif key == ord("c"):
      pause = False

    red_area = openCv.countNonZero(mask)

    # Controle dos Atuadores
    if not pause:
      if circleHistory is None:
        if not have_detect:
          robot.turn_right(SEARCH_SPEED)
        elif red_area >= THRES_RED:
          robot.stop()
        else:
          if last_error_x is not None and last_error_x < 0:
            robot.turn_left(SEARCH_SPEED)
          else:
            robot.turn_right(SEARCH_SPEED)
      else:
        robot.move(speed_left=left_speed, speed_right=right_speed)
    else:
      robot.stop()

  robot.cleanup()
  picam.cleanup()
  openCv.destroyAllWindows()