from roverlib.modules.movement.robot import Robot
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from pathlib import Path
import numpy
import cv2 as openCv

if __name__ == "__main__":
    
    # Carrega configuraçôes de hardware
    config = Config(
        Path(__file__).parent / "config.yaml"
    )
    
    config_cam = config.get("camera")
    config_motor = config.get("motor")
    
    # Inicia motores
    robot = Robot(
        left=config_motor["left"],
        right=config_motor["right"],
    )
    speed = 50 # Velocidade inicial
    
    try:
        from roverlib.plugins.camera.autoFocus import AfCamera, AfModeEnum
        camera = AfCamera(
            height=config_cam["resolution"]["h"],
            width=config_cam["resolution"]["w"],
            fps=config_cam["fps"]
        )
        
        camera.start()
        camera.set_afMode(AfModeEnum.Continuous)
        camera.set_brightness(config_cam["brigh"])
        camera.set_contrast(config_cam["contrast"])
        camera.set_saturation(config_cam["saturation"])
    
    except:
        try:
            camera = Camera(
                height=config_cam["resolution"]["h"],
                width=config_cam["resolution"]["w"],
                fps=config_cam["fps"]
            )
            
            camera.start()
            camera.set_brightness(config_cam["brigh"])
            camera.set_contrast(config_cam["contrast"])
            camera.set_saturation(config_cam["saturation"])
            cam_available = True
            
        except: 
            print("Não foi possivel configura a câmera.")
            cam_available = False 
            
    # Cria uma imagem preta
    frame_black = numpy.full(
        (config_cam["resolution"]["h"], config_cam["resolution"]["w"], 3), (0, 0, 0)
    )
    
    # Texto para mostrar na janela que não foi possivel configura a camera 
    txt = "Sem acesso a câmera!"
    openCv.putText(frame_black, txt, (10,35), openCv.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, (255, 255, 255), 2)
    openCv.imshow("Rover", frame_black)
    
    while True:
        if cam_available:
            frame = camera.get_frame()

            if frame is not None:
                txt = ""
                openCv.putText(frame, txt, (10,35), openCv.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, (255, 255, 255), 2)
                openCv.imshow("Rover", frame)
           
        speed = max(0, min(speed, 100))        
        
        key = openCv.waitKey(1) & 0xFF # Espera resposta do teclado
        
        if key == ord("w"):
            robot.forward(speed)
            pass
        
        elif key == ord("a"):
            robot.turn_left(speed)
            pass
        
        elif key == ord("d"):
            robot.turn_right(speed)
            pass
        
        elif key == ord("s"):
            robot.backward(speed)
            pass
            
        elif key == ord("e"):
            speed = max(0, min(speed + 10, 100))
        
        elif key == ord("r"):
            speed = max(0, min(speed - 10, 100))
        
        elif key == ord("q"):
            break
    
        else:
            pass
            robot.stop()
        
        print(speed)
    
    robot.cleanup()
    camera.cleanup()
    openCv.destroyAllWindows()