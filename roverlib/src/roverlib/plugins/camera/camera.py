import cv2 as openCV
from .cameraInterface import CameraInterface
from .exceptions import CameraNotStart, CameraNotAvailable
from roverlib.modules.processing.processing_image import ProcessingImage
from time import time, sleep
from enum import IntEnum

try:
    # tenta importa a biblioteca libcamera, especifica da Raspbarry Pi
    from libcamera import Transform # type: ignore
    availableLibcamera = True
except (ImportError, ModuleNotFoundError):
    availableLibcamera = False

try:
    # Tenta importar a biblioteca picamera2, específica da Raspberry Pi
    from picamera2 import Picamera2, Preview
    from picamera2.encoders import H264Encoder, Quality
    from picamera2.outputs import FileOutput
    availablePicamera2 = True
except (ImportError, ModuleNotFoundError):
    availablePicamera2 = False

# Nome padrão dos plugins: a câmera da Raspberry Pi precisa das duas bibliotecas
HARDWARE_AVAILABLE = availablePicamera2 and availableLibcamera

class CameraFormat(IntEnum):
    """Conversões de cor do OpenCV aceitas por `Camera.set_format()`."""
    BGR = openCV.COLOR_RGB2BGR
    Gray = openCV.COLOR_RGB2GRAY
    HSV = openCV.COLOR_RGB2HSV

class Camera(CameraInterface):
    """
    Câmera da Raspberry Pi (CSI), controlada pela Picamera2 (drivers libcamera).

    Os frames são arrays NumPy em **BGR**, o padrão do OpenCV: podem ir direto para
    `cv2.imshow()` e para as funções de `ProcessingImage`. No Rover, a câmera é uma
    Arducam IMX519; para controlar o foco dela, use `AfCamera`.

    Exemplo:

    ```python
    cam = Camera(height=480, width=640)
    cam.start()
    frame = cam.get_frame()
    cam.cleanup()
    ```

    Prefira `open_camera()` ou a seção `camera:` do config.yaml, que escolhem a
    webcam automaticamente no PC.
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
        Configura a câmera. Chame `start()` antes de capturar.

        Args:
            height (int): altura dos frames, em pixels.
            width (int): largura dos frames, em pixels.
            fps (int): quadros por segundo. Padrão 30.
            index (int): qual câmera usar, se houver mais de uma. Padrão 0.
            format (CameraFormat, optional): conversão de cor aplicada aos frames. Padrão: nenhuma (BGR).
            horizontalFlip (bool): espelha a imagem na horizontal. Padrão False.
            verticalFlip (bool): espelha a imagem na vertical. Padrão False.
                Com a câmera de cabeça para baixo, use os dois flips.

        Raises:
            CameraNotAvailable: a Picamera2 ou a libcamera não estão instaladas (por exemplo, no PC).
        """

        if not availablePicamera2:
            raise CameraNotAvailable("Não foi possivel importar o modulo picamera2")

        if not availableLibcamera:
            raise CameraNotAvailable("Não foi possivel importar o modulo libcamera")

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
        """Inicia a captura. Chamar de novo com a câmera já ligada não faz nada."""

        if not self.runing:
            self.picam2.start() # Inicia a câmera
            self.runing = True
            return

    def stop(self):
        """Para a captura (a câmera pode ser iniciada de novo com `start()`)."""

        if self.runing:
            self.picam2.stop() # Para câmera
            self.runing = False

    def set_exposure(self, expousure_us: int, gain: float):
        """
        Fixa a exposição manualmente, desligando a exposição automática.

        Args:
            expousure_us (int): tempo de exposição de cada frame, em microssegundos.
                Valores maiores clareiam a imagem, mas borram objetos em movimento.
            gain (float): ganho analógico do sensor (1.0 = sem ganho). Valores maiores
                clareiam a imagem, com mais ruído.

        Para voltar à exposição automática, use `enable_exposure()`.
        """

        self.picam2.set_controls(
            {
                "AeEnable": False,
                "ExposureTime": expousure_us,
                "AnalogueGain": gain
            }
        )

    def enable_exposure(self):
        """Volta à exposição automática (desfaz `set_exposure()`)."""
        self.picam2.set_controls(
            {
                "AeEnable": True
            }
        )

    def set_FPS(self, fps: int):
        """
        Muda a taxa de quadros da câmera.

        Args:
            fps (int): nova taxa de quadros por segundo.
        """

        self.fps = fps
        self.picam2.controls.FrameRate = self.fps

    def set_brightness(self, brightness: float = 0.0):
        """
        Ajusta o brilho da imagem.

        O ajuste soma aproximadamente `255 × brightness` a cada pixel: valores pequenos
        (±0.1) já fazem bastante diferença, e -0.3 deixa uma sala comum quase preta.

        Args:
            brightness (float): de -1.0 (mais escuro) a 1.0 (mais claro). Padrão 0.0 (sem ajuste).

        Raises:
            ValueError: valor fora do intervalo [-1.0, 1.0].
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
        Ajusta o contraste da imagem.

        Args:
            contrast (float): de 0.0 a 32.0. 1.0 (padrão) mantém a imagem original;
                valores maiores aumentam a diferença entre claros e escuros.

        Raises:
            ValueError: valor fora do intervalo [0, 32].
        """

        if 0 > contrast or contrast > 32.0:
            raise ValueError("O valor do contrast deve ser um float no intervalo [0, 32]")

        # Configura o contrast
        self.picam2.set_controls(
            {
                "Contrast": contrast
            }
        )

    def set_saturation(self, saturation):
        """
        Ajusta a saturação (intensidade das cores) da imagem.

        Args:
            saturation (float): de 0.0 (preto e branco) a 32.0. 1.0 mantém as cores originais.

        Raises:
            ValueError: valor fora do intervalo [0, 32].
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
        Recorta os próximos frames para uma região da imagem.

        Args:
            region_interest (tuple[int, int, int, int]): `(x, y, largura, altura)` da região, em pixels,
                a partir do canto superior esquerdo `(x, y)`.

        Para voltar à imagem inteira, use `clear_region_interest()`.
        """
        self.region_interest = region_interest

    def clear_region_interest(self):
        """Remove o recorte definido por `set_region_interest()`."""
        self.region_interest = None

    def set_format(self, format: CameraFormat):
        """
        Define uma conversão de cor para os frames.

        Args:
            format (CameraFormat): conversão do OpenCV (`CameraFormat.BGR`, `.Gray` ou `.HSV`).
        """
        self.format = format

    def get_frame(self):
        """
        Captura um frame.

        Returns:
            numpy.ndarray: imagem `(altura, largura, 3)` em **BGR**, já recortada pela região de interesse, se houver.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
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
        Captura um frame e o instante da captura.

        Returns:
            tuple: `(frame, instante)`, com o instante em segundos (`time.time()`).
        """

        return self.get_frame(), time()

    def get_picture(self, file:str):
        """
        Mostra a imagem da câmera em uma janela e salva uma foto quando a tecla **s** é pressionada.

        Args:
            file (str): caminho do arquivo de imagem (ex.: `"foto.jpg"`).

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
        """

        if not self.runing:
            raise CameraNotStart("Câmera não iniciada")

        while True:

            frame = self.get_frame()

            openCV.imshow("Frame", frame)

            key = openCV.waitKey(10) & 0xFF

            if key == ord('s'):
                openCV.imwrite(file, frame)
                break

        openCV.destroyAllWindows()

    def get_video(self, file:str, t:float):
        """
        Grava um vídeo H.264 por um tempo fixo, com pré-visualização na tela.

        Args:
            file (str): caminho do arquivo de vídeo (ex.: `"video.h264"`).
            t (float): duração da gravação, em segundos.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
        """
        if not self.runing:
            raise CameraNotStart("Câmera não iniciada")

        self.picam2.start_preview(Preview.QTGL) # Inicia pre-vizualização
        encoder = H264Encoder() # Encoder h264
        output = FileOutput(file) # Saida para o arquivo

        self.picam2.start_recording(encoder, output, Quality.HIGH) #  inicia gravação
        sleep(t) # Tempo de gravação
        self.picam2.stop_recording() # termina gravação

    def metadata(self):
        """
        Lê os metadados do frame mais recente.

        Returns:
            dict: valores como `ExposureTime`, `AnalogueGain`, `LensPosition` e `Lux`.
        """

        return self.picam2.capture_metadata()

    def isRunning(self) -> bool:
        """
        Indica se a câmera está capturando.

        Returns:
            bool: True entre `start()` e `stop()`.
        """
        return self.runing

    def cleanup(self):
        """Para a câmera e libera os recursos. Pode ser chamado mais de uma vez."""
        self.stop()