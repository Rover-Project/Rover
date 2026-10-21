import cv2 as openCV
from pathlib import Path
from roverlib.utils.config_manager import Config

class ManualFocusController:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        cam_config = self.config.get("camera")
        self.position = 0
        self.camera = None

        try:
            from roverlib.plugins.camera.autoFocus import AfCamera, AfModeEnum, AfSpeedEnum
            
            self.camera = AfCamera(
                height=cam_config["resolution"]["h"],
                width=cam_config["resolution"]["w"],
                afMode=AfModeEnum.Manual,
                afSpeed=AfSpeedEnum.Normal
            )
            self.camera.start()

            self.camera.set_brightness(cam_config.get("brigh", 0))
            self.camera.set_contrast(cam_config.get("contrast", 1))
            self.camera.set_saturation(cam_config.get("saturation", 1))
            print("Câmera com foco manual iniciada com sucesso.")
        except Exception as error:
            print(f"Erro ao configurar câmera com foco automático: {error}")

    def run(self):
        if self.camera is None:
            print("Encerrando execução pois a câmera não pôde ser inicializada.")
            return

        print("Use 'w' para aproximar o foco, 's' para distanciar e 'q' para sair.")
        while True:
            frame = self.camera.get_frame()

            if frame is not None:
                openCV.imshow("Frame - Ajuste Manual", frame)

            key = openCV.waitKey(10) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("w"):
                self.position = min(self.position + 1, 10)
                self.camera.set_focus_position(self.position)
                print(f"Posição do Foco: {self.position}")
            elif key == ord("s"):
                self.position = max(self.position - 1, 0)
                self.camera.set_focus_position(self.position)
                print(f"Posição do Foco: {self.position}")

    def cleanup(self):
        print("\nDesligando a câmera...")
        if self.camera is not None:
            self.camera.cleanup()
        openCV.destroyAllWindows()
