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
    HEIGHT = 4656
    WIDTH = 3496
    
    b = 0 
    s = 0
    c = 0
    
    frame = None

    # Inicializa câmera
    try:
        camera = AfCamera(HEIGHT, WIDTH)
        camera.start()
    except:
        raise RuntimeError("Erro ao abrir câmera")


    while True:
        frame = camera.get_frame()

        if frame is not None:
            openCv.imshow("Rover", frame)

            key = openCv.waitKey(10) & 0xFF

            if key == ord("w"):
                servos.forward(channels=tuple([SERVO_V]), speed=SPEED)

            elif key == ord("s"):
                servos.backward(channels=tuple([SERVO_V]), speed=SPEED)

            elif key == ord("a"):
                servos.forward(channels=tuple([SERVO_H]), speed=SPEED)

            elif key == ord("d"):
                servos.backward(channels=tuple([SERVO_H]), speed=SPEED)

            elif key == "z":
                b += 0.1
                camera.set_brightness(b)
            
            elif key == "x":
                b -= 0.1   
                camera.set_brightness(b)
                
            elif key == "c":
                s += 0.1
                camera.set_saturation(s)
            
            elif key == "v":
                s -= 0.1
                camera.set_saturation(s)
            
            elif key == "b":
                c += 0.1
                camera.set_contrast(c)
                
            elif key == "n":
                c -= 0.1
                camera.set_contrast(c)

            elif key == ord("q"):
                break

            else:
                servos.stop(channels=tuple([SERVO_V, SERVO_H]))

file = input("Nome do arquivo: ")

camera.cleanup()
openCv.imwrite(file, frame)
openCv.destroyAllWindows()