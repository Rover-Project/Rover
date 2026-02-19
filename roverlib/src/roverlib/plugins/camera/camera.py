import cv2 as openCV
from .cameraInterface import CameraInterface
from .exceptions import CameraNotStart
from roverlib.modules.processing.processing_image import ProcessingImage
from time import time
from enum import Enum

try: 
    # tenta importa a biblioteca libcamera, especifica da Raspbarry Pi
    from libcamera import Transform # type: ignore
    availableLibcamera = True
except (ImportError, ModuleNotFoundError):
    availableLibcamera = False
    
try:
    # Tenta importar a biblioteca picamera2, específica da Raspberry Pi
    from picamera2 import Picamera2 # type: ignore
    availablePicamera2 = True
except (ImportError, ModuleNotFoundError):
    availablePicamera2 = False
    
class CameraFormat(Enum):
    """
    Enum para conversão de formato de rgb para bgr, gray ou hsv
    """
    BGR = openCV.COLOR_RGB2BGR
    Gray = openCV.COLOR_RGB2GRAY
    HSV = openCV.COLOR_RGB2HSV

class Camera(CameraInterface):
    """
    Plugin de câmera. Realiza o controle dos hardwares de câmera. 
    Versão génerica para câmeras simples usa como API o módulo Picamera2 que usa os drivers da libcamera na raspberry pi 5. 
    """
    
    def __init__(
        self, 
        height:int, 
        width:int,
        fps: int = 30, 
        index: int = 0,
        format=None,
        horizontalFlip: bool = False,
        verticalFlip: bool = False 
    ):
        """
        Realiza a configuração inicial da câmera.
        
        Args:
            height (int): altura dos frames
            width (int): largura dos frames
            fps (int, optional): taxa de quadros. Valor padrão 30.
            index (int, optional): index da câmera que deseja usar. Valor padrão 0.
            format (str, optional): Formato de captura dos frames. Valor padrão "rgb".
            horizontalFlip (bool, optional): Espelha o eixo horizontal. Valor padrão False.
            verticalFlip (bool, optional): Espelha o eixo vertical. Valor padrão False.

        Raises:
            ModuleNotFoundError: Erro disparado caso não seja possível importar o módulo picamera2
            ModuleNotFoundError: Erro disparado caso não seja possível importar o módulo libcamera
        """
        
        if not availablePicamera2:
            raise ModuleNotFoundError("Não foi possivel importa o modulo picamera2")
        
        if not availableLibcamera:
            raise ModuleNotFoundError("Não foi possivel importar o modulo libcamera")
        
        self.size = (width, height) # tamanho da imagem
        self.fps = fps # taxa de frames
        self.format = format # formato das imagens capturadas
        self.index = index # index da câmera que deseja usar 
        self.region_interest = None # Região de interesse na captura 
        self.runing = False # Controla se a câmera estar em funcionamento
        
        self.picam2 = Picamera2(index) # Instância câmera
        
        self.config = self.picam2.create_video_configuration( # type: ignore
            main={
                    "size": self.size, # tamanho da imagem
                    "format": "RGB888" # formato de captura 
                },   
            transform=Transform(
                hflip=horizontalFlip, # Espelha de forma horizontal
                vflip=verticalFlip # Espelha de forma vertical
            )
        )
        
        self.picam2.configure(self.config) # Configura câmera
        
        self.picam2.set_controls(
            {
                "FrameRate": fps, # Taxa de frame
                "AeEnable": True, 
                "AwbEnable": True
            }
        )
        
    def start(self):
        """
        Inicia o funcionamento da câmera com a configuração definida no construtor.
        """
        
        if not self.runing:
            self.picam2.start() # Inicia a câmera
            self.runing = True
            return
            
    def stop(self):
        """
        Encerra o funcionamento da câmera.
        """
        
        if self.runing:
            self.picam2.stop() # Para câmera
            self.runing = False
            
    def set_exposure(self, expousure_us: int, gain: float):
        """
        Muda configuração de tempo de exposição à luz na aquisição de frames. Por padrão é automática.
        Args:
            expousure_us (int): _description_
            gain (float): _description_
        """
        
        self.picam2.set_controls(
            {
                "AeEnable": False,
                "ExposureTime": expousure_us,
                "AnalogueGain": gain
            }
        )
    
    def enable_exposure(self):
        """
            Desativa configuração de tempo de exposição manual na aquisição de frames. 
        """
        self.picam2.set_controls(
            {
                "AeEnable": True
            }
        )
        
    def set_FPS(self, fps: int):
        """
        Muda a taxa de quadros da câmera.
        Args:
            fps (int): Nova taxa de quadros.
        """
        
        self.fps = fps
        self.picam2.controls.FrameRate = self.fps
        
    def set_brightness(self, brightness: float = 0.0):
        """
        Define um valor para o brilho das imagens da câmera
        Args:
            brightness (float, optional): Valor do brilho. Valor padrão 0.0.

        Raises:
            ValueError: Exceção lançada caso o brightness estiver fora do intervalo [-1.0, 1.0]
        """
        
        if -1.0 > brightness or brightness > 1.0:
            raise ValueError("O valor para o brilho deve ser um float no intervalo [-1.0, 1.0]")
        
        # Configura o brilho
        self.picam2.set_controls(
            {
                "Brightness": brightness
            }
        )
    
    def set_contrast(self, contrast: float = 1):
        """
        Define o contraste das imagens da câmera
        Args:
            contrast (float, optional): Valor para o contrast. Valor padrão 1.

        Raises:
            ValueError: Exceção lançada caso o contraste estiver fora do intervalo [0, 32]
        """
        
        if 0 > contrast or contrast > 32.0:
            raise ValueError("O valor do contrast deve ser um float no intervalo [0, 32]")
        
        # Configura o contrast
        self.picam2.set_controls(
            {
                "Constrast": contrast
            }
        )
    
    def set_saturation(self, saturation):
        """
        Define a saturação das imagens da câmera
        Args:
            contrast (float, optional): Valor para a saturação. Valor padrão 1.

        Raises:
            ValueError: Exceção lançada caso a saturação estiver fora do intervalo [0, 32]
        """
        
        if 0 > saturation or saturation > 32.0:
            raise ValueError("O valor da saturação deve ser um float no intervalo [0, 32]")
        
        # Configura o contrast
        self.picam2.set_controls(
            {
                "Saturation": saturation
            }
        )
    
    def set_region_interest(self, region_interest: tuple[int, int, int, int]):
        """
        Define uma região de interesse para corte na aquisição de frames.
        Args:
            region_interest (tuple[int, int, int, int]): coordenadas de corte 0 = x_start, 1 = y_start, 2 = x_end, 3 = y_end
        """
        self.region_interest = region_interest

    def clear_region_interest(self):
        """
        Limpa região de interesse
        """
        self.region_interest = None
        
    def set_format(self, format: CameraFormat):
        """
        Define o formato do frame na aquisição
        Args:
            format (str): Formato do frame.
            
        Raises:
            ValueError: Dispara exceção se o formato não estiver dentre ["rgb", "bgr", "hsv", "gray"]
        """
        self.format = format
            
    def get_frame(self):
        """
        Captura um único frame da câmera.

        Retorna:
            numpy.array: O frame capturado como um array NumPy no formato RGB.
        """
        
        if not self.runing:
            raise CameraNotStart("Você não iniciou a câmera")
        
        frame = self.picam2.capture_array("main") # Captura um frame
        
        if self.region_interest is not None:
            frame = ProcessingImage.cutImage(frame, self.region_interest) # Corta frame na região de interesse
        
        if self.format is not None:
            openCV.cvtColor(frame, self.format) # type: ignore
        
        return frame
    
    def get_frame_time(self):
        """
        Captura um frame e retorna o momento em que ele foi capturado
        Returns:
            (numpy array, time): tupla com o frame e o momento de captura.
        """
        
        return self.get_frame(), time()
        
    def get_picture(self, file:str):
        """
        Captura imagem e salva.
        Args:
            file (str): Caminho para salvar imagem.
        """
        
        if not self.runing:
            raise CameraNotStart("Câmera não iniciada")
        
        try:
            self.picam2.start_and_capture_file(file) # captura e salva imagem com o path do file
            print('Imagem capturada com sucesso!')
        except:
            print("Erro ao capturar imagem.")
        
    def get_video(self, file:str, duration:int):
        """
        Captura video e salva.
        Args:
            file (str): caminho para salvar video.
            duration (int): duração do video.
        """
        
        if not self.runing:
            raise CameraNotStart("Câmera não iniciada") 
        
        try:
            self.picam2.start_and_record_Video(file, duration)
            print("Video gravado com sucesso!")
        except:
            print("Erro ao capturar Video.")
            
    def metadata(self):
        """
        Retorna os metadados da câmera.
        Returns:
            _type_: _description_
        """
        
        return self.picam2.capture_metadata()

    def isRunning(self) -> bool:
        """
        Retorna se a câmera está ativa
        Returns:
            bool: Se a câmera está ativa
        """
        return self.runing

    def cleanup(self):
        """
        Libera os recursos da câmera.
        """
        self.stop()