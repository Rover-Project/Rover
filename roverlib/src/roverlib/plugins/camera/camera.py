import cv2
from roverlib.src.roverlib.utils.config_manager import Config
from .cameraInterface import CameraInterface

try:
    # Tenta importar a biblioteca picamera2, específica da Raspberry Pi
    from picamera2 import Picamera2 # type: ignore
    availablePicamera = True
except (ImportError, ModuleNotFoundError):
    availablePicamera = False

# Carrega configuração da câmera
CAMERA_RESOLUTION = tuple(Config.get("camera")["resolution"])
CAMERA_FPS = int(Config.get("camera")["fps"])
CAMERA_PREVIEW_RESOLUTION = tuple(Config.get("camera")["preview_resolution"])

class Camera(CameraInterface):
    """
    Módulo para gerenciar a câmera do Rover, capturar e fornecer frames
    para o módulo de visão computacional.
    """
    def __init__(self, height, width, analogic=1.5, exposure = 30000, lighConfig=False):
        
        if not availablePicamera:
            raise ModuleNotFoundError("Não foi possivel importa o modulo Picamera2")
        
        """Inicializa e configura a câmera."""
        self.picam2 = Picamera2()
        
        # Usamos o modo 'preview' para processamento em tempo real
        config = self.picam2.create_preview_configuration( # type: ignore
            main={
                    "size": (height, width), "format": "RGB888"
                },    
        )
        
        #  Configuração de iluminação
        if lighConfig:
            self.picam2.set_controls( # type: ignore
                {
                "AnalogueGain": 1.5,   # controla amplificação do sensor, analogic < 1 = mais escuro
                "ExposureTime": 30000, # em microssegundos, menor = mais escuro
            }
        )
        self.picam2.configure(config)
        self.picam2.start()
        print("Câmera inicializada.")
    
    def get_frame(self):
        """
        Captura um único frame da câmera.

        Retorna:
            numpy.array: O frame capturado como um array NumPy no formato BGR.
        """
        # A picamera2 captura em formato RGB por padrão
        frame_rgb = self.picam2.capture_array("main")
        
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    
        return frame_bgr

    def get_preview_resolution(self):
        """Retorna a resolução de preview configurada."""
        return CAMERA_PREVIEW_RESOLUTION

    def cleanup(self):
        """Libera os recursos da câmera."""
        print("Liberando recursos da câmera...")
        self.picam2.stop()