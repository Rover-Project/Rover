import cv2 as openCV
from pathlib import Path
from roverlib.utils.config_manager import Config

class ContinuousFocusApp:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        cam_config = self.config.get("camera", {})
        
        self.height = cam_config.get("resolution", {}).get("h", 1080)
        self.width = cam_config.get("resolution", {}).get("w", 1080)
        self.camera = None
        
        try:
            from roverlib.plugins.camera.autoFocus import AfCamera
            
            # Instancia a câmera com foco contínuo automático por padrão na classe AfCamera
            self.camera = AfCamera(height=self.height, width=self.width, verticalFlip=True)
            self.camera.start()
            
            # Aplica configurações visuais se suportado
            if hasattr(self.camera, 'set_brightness'):
                self.camera.set_brightness(cam_config.get("brigh", 0.25))
                self.camera.set_contrast(cam_config.get("contrast", 1))
                self.camera.set_saturation(cam_config.get("saturation", 1))
                
            print("Câmera com Foco Contínuo iniciada com sucesso.")
        except Exception as e:
            print(f"Erro ao inicializar a câmera: {e}")

    def run(self):
        if self.camera is None:
            print("Encerrando execução pois a câmera não pôde ser iniciada.")
            return

        print("Pressione 's' para salvar uma foto ou 'q' para sair.")
        while True:
            frame = self.camera.get_frame()
            
            if frame is not None:
                openCV.imshow("Frame - Foco Continuo", frame)

            key = openCV.waitKey(10) & 0xFF
            
            if key == ord("q"):
                break
            elif key == ord("s"):
                if frame is not None:
                    openCV.imwrite('foto.jpeg', frame)
                    print("Foto salva como 'foto.jpeg'. Encerrando programa...")
                else:
                    print("Erro: Nenhum frame para salvar.")
                break

    def cleanup(self):
        print("\nDesligando a câmera...")
        if self.camera is not None:
            self.camera.cleanup()
        openCV.destroyAllWindows()
