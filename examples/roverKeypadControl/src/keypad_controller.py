import cv2 as openCv
from pathlib import Path
from roverlib.modules.movement.robot import Robot
from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.utils.config_manager import Config

class KeypadController:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        
        # Configuração da câmera
        self.height = 640
        self.width = 640
        self.camera = AfCamera(self.height, self.width)
        
        # Configuração dos motores
        pins_motors = self.config.get("gpio")["motor"]
        self.robot = Robot(left=pins_motors["left"], right=pins_motors["right"])
        
        # Estado inicial
        self.speed = 50 

    def run(self):
        try:
            self.camera.start()
            print("Câmera e motores iniciados. Pressione 'q' na janela de vídeo para sair.")
        except Exception as e:
            raise RuntimeError(f"Erro ao abrir câmera: {e}")

        while True:
            frame = self.camera.get_frame()

            if frame is not None:
                openCv.imshow("Rover - Controle Manual", frame)

                # Espera 10ms pela resposta do teclado
                key = openCv.waitKey(10) & 0xFF 

                if key == ord("w"):
                    self.robot.forward(self.speed)
                elif key == ord("a"):
                    self.robot.turn_left(self.speed)
                elif key == ord("d"):
                    self.robot.turn_right(self.speed)
                elif key == ord("s"):
                    self.robot.backward(self.speed)
                elif key == ord("e"):
                    self.speed = max(0, min(self.speed + 10, 100))
                    print(f"Velocidade aumentada: {self.speed}")
                elif key == ord("r"):
                    self.speed = max(0, min(self.speed - 10, 100))
                    print(f"Velocidade reduzida: {self.speed}")
                elif key == ord("q"):
                    break
                else:
                    self.robot.stop()

    def cleanup(self):
        print("\nDesligando o Rover...")
        self.robot.cleanup()
        self.camera.cleanup()
        openCv.destroyAllWindows()