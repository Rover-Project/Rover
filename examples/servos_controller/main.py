from roverlib.plugins.PCAServos.pcaServos import PCAServos
from roverlib.plugins.camera.autoFocus import AfCamera
import cv2 as openCv

if __name__ == "__main__":
    FREQUENCY_SERVOS = 50 # Frequencia do PWM
    
    SPEED = 50 # Velocidade padrao
    SERVO_V = 1 # Servo vertival 
    SERVO_H = 0 # Servo Horizontal
    
    # Instancia o controle para os servos
    servos = PCAServos(
        FREQUENCY_SERVOS
    )
    
    # Tamanho de aquisicao de imagens 
    HEIGHT = 1080
    WIDTH = 1080

    # Inicializa câmera
    try:
        camera = AfCamera(HEIGHT, WIDTH)
        camera.start()
    except:
        raise RuntimeError("Erro ao abrir câmera")

    try:
        while True:
            frame = camera.get_frame()

            if frame is not None:
                openCv.imshow("Rover", frame)

                key = openCv.waitKey(10) & 0xFF

                if key == ord("w"):
                    servos.forward(channels=tuple(SERVO_V), speed=SPEED)

                elif key == ord("s"):
                    servos.backward(channels=tuple(SERVO_V), speed=SPEED)

                elif key == ord("a"):
                    servos.forward(channels=tuple(SERVO_H), speed=SPEED)

                elif key == ord("d"):
                    servos.backward(channels=tuple(SERVO_H), speed=SPEED)

                elif key == ord("q"):
                    break

                else:
                    servos.stop(channels=tuple(SERVO_V, SERVO_H))
                   
    except KeyboardInterrupt:
        print("Encerrando.")

    finally:
        servos.cleaup()
        camera.cleanup()
        openCv.destroyAllWindows()