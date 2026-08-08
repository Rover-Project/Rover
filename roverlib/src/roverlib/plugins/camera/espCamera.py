from .exceptions import EspCamNotStart
from .cameraInterface import CameraInterface
from time import time
import requests
import cv2
import threading

class EspCamera(CameraInterface):
    """
    Plugin feito para controle de ações realizadas pela Esp32Cam.
    """

    def __init__(self, esp_ip: str):
        """
        Realiza a configuração inicial da câmera.
        """    
        
        self.ip = esp_ip # ip da esp32 
        self.url_stream = f"http://{esp_ip}:81/stream" # url do stream
        self.url_control = f"http://{esp_ip}/control" # url de controle

        self.capture = None
        self.started = False
        self.thread = None

        # Variáveis para estado do frame capturado
        self.frame = None
        self.frame_time = 0.0
        self.lock = threading.Lock()

    def _send_command_to_espCam(self, variable_swap: str, new_value) -> tuple[bool, int]:
        """
        Envia uma requisição HTTP para a esp32Cam com objetivo de alterar seus parâmetros em tempo de execução.
        Args:
            variable_swap (str): Parâmetro que deseja mudar 
            new_value (_type_): Valor novo para o parâmetro passado

        Returns:
            tuple[bool, int]: estado da request, se realizou a atualização e o código da request.
        """
        
        try:
            answer = requests.get(
                self.url_control, # endpoint de controle
                params={'var': variable_swap, 'val': new_value}, # corpo do request
                timeout=1 # tempo de espera
            )
            
            if answer.status_code == 200: 
                return True, 200 # sucesso
                 
            else: 
                return False, answer.status_code # Falha com código personalizado
                
        except Exception:
            return False, 404 # Servidor da esp32Cam não existe

    def start(self) -> bool:
        """
        Método para iniciar o funcionamento da câmera.

        Raises:
            EspCamNotStart: Caso o fucionamento da câmera não inicie de forma correta.

        Returns:
            isStarter: Valor bool que indiaca se o funcionamento iniciou de forma correta
        """

        if self.started:
            return True
        
        self.capture = cv2.VideoCapture(self.stream_url) # Inicia o stream na url 
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) # minimiza o tamanho do Buffer para mais perfomance

        if not self.capture.isOpened():
            raise EspCamNotStart("A câmera não iniciou de forma correta!") # Camera não iniciou
        
        self.started = True
        self.thread = threading.Thread(target=self._update, args=()) # separa uma thread para fazer os requests
        self.thread.daemon = True
        self.thread.start() # inicia a thread
        return True
    
    def _update(self):
        """
        Método para atualizar continuamente o valor dos frames da câmera.
        """
        
        while self.started:
            try:
                ret, frame = self.capture.read()
                if not ret:
                    print("Falha ao receber frame. Verifique a conexão ou o IP passado")
                    time.sleep(0.2)
                    continue
                
            except Exception as e:
                print(e)

            with self.lock:
                self.frame = frame
                self.frame_time = time.time()

    def stop(self):
        """
        Encerra o funcionamento da camera.
        """
        
        if self.started:
        
            self.starded = False
            if self.thread is not None:
                self.thread.join(timeout=2) # aguarda a thread finalizar com segurança
            
            if self.capture is not None:
                self.capture.release() # libera recursos da camera 

    def quality_update(self, val: int):
        """
        Ajusta a qualidade dos frames da camera.

        Args:
            val (int): Novo valor para o parâmetro de qualidade, quanto menor mais qualidade nos frames.

        Raises:
            ValueError: Se o valor para a qualidade estiver fora do intervalo [10,63].
        """

        if val < 10 or val > 63: 
            raise ValueError("O valor para o parâmetro de qualidade  deve estar no interalo [10,63]")
        
        self._send_command_to_espCam("quality", val) # envia request para atualizar o parâmetro

    def set_brightness(self, val: int):
        """
        Ajusta o brilho dos frames da camera.

        Args:
            val (int): Novo valor para o parâmetro de brilho, quanto menor menos brilho nos frames.

        Raises:
            ValueError: Se o valor para a qualidade estiver fora do intervalo [-2,2].
        """

        if val < -2 or val > 2: 
            raise ValueError("O valor para o parâmetro de brilho deve estar no interalo [-2,2]")
        
        self._send_command_to_espCam("brightness", val) # envia request para atualizar o parâmetro
    
    def set_contrast(self, val: int):
        """
        Ajusta o contraste dos frames da camera.

        Args:
            val (int): Novo valor para o parâmetro de contraste, quanto menor menos contraste nos frames.

        Raises:
            ValueError: Se o valor para o contraste estiver fora do intervalo [-2,2].
        """

        if val < -2 or val > 2:
            raise ValueError("O valor para o parâmetro de contraste deve estar no interalo [-2,2]")
        
        self._send_command_to_espCam("contrast", val)

    def set_saturation(self, val: int):
        """
        Ajusta a saturação dos frames da camera.

        Args:
            val (int): Novo valor para o parâmetro de saturação, quanto menor menos saturação nos frames.

        Raises:
            ValueError: Se o valor para a saturação estiver fora do intervalo [-2,2].
        """

        if val < - 2 or val > 2:
            raise ValueError("O valor para o parâmetro de saturação deve estar no interalo [-2,2]")
        
        self._send_command_to_espCam("saturation", val)

    def set_white_balance(self, val: int):
        """
        Ativa ou desativa o balanço de branco automático da Câmera.

        Args:
            val (int): 1 para ativado, 0 para desativado.

        Raises:
            ValueError: Se o valor for diferente de 1 e 0.
        """
        
        if val != 0 or val != 1:
            raise ValueError("O valor para white balance deve ser 1 ou 0")
        
        self._send_command_to_espCam("awb", val)
        

    def set_mode_of_awb(self, val: int):
        """
        Altera o tipo de balanço de branco automático.

        Args:
            val (int):      
                - 0: Auto;
                - 1: Ensolarado;
                - 2: Nublado;
                - 3: Fluorescente;
                - 4: Incandescente.

        Raises:
            ValueError: Se o modo de balanço de branco for inválido.
        """
        
        if val < 0 or val > 4:
            raise ValueError("O modo do balanço de branco dever ser um inteiro no intervalo [0,4]")
        
        self._send_command_to_espCam("awb", 1) # ativa o balanço de branco
        self._send_command_to_espCam("wb_mode", val) # altera o valor

    def set_auto_exposition(self, val: int):
        """
        Ativa ou desativa a exposição automática.

        Args:
            val (int): 1 para ativado, 0 para desativado.

        Raises:
            ValueError: Se o valor for diferente de 1 e 0.
        """
        
        if val != 0 or val != 1:
            raise ValueError("O valor para exposição automática deve ser 1 ou 0")
        
        self._send_command_to_espCam("aec", val)
      
    def set_framesize(self, val: int):
        """
        Altera a proporção da imagem capturada.

        Args:
            val (int):      
                - 4: (640 X 480)
                - 5: (400 X 296)
                - 6: (320 X 240)
                - 7: (240 X 240)
                - 8: (800 X 600)
                - 9: (1024 X 768)
                - 10: (1280 X 1024)
                - 11: (1600 X 1200)

        Raises:
            ValueError: Se a proporção for inválida.
        """

        if val < 4 or val > 11:
            raise ValueError("O valor para a proporção do frame deve ser um inteiro no intervalo [4,11]")
        
        self._send_command_to_espCam("framesize", val)

    def h_flip(self, val: int):
        """
        Muda o valor do flip horizontal.

        Args:
            val (int): Valor para o flip horizontal, 0 para desativar 1 para ativar.

        Raises:
            ValueError: Se o valor para o flip horizontal for inválido.
        """
        
        if val != 0 or val != 1:
            raise ValueError("O valor inválido para o flip horizontal, o flip deve ser 1 ou 0")

        self._send_command_to_espCam("hmirror", val)

    def v_flip(self, val: int):
        """
        Muda o valor do flip vertical.

        Args:
            val (int): Valor para o flip vertical, 0 para desativar 1 para ativar.

        Raises:
            ValueError: Se o valor para o flip vertical for inválido.
        """

        if val != 0 or val != 1:
            raise ValueError("O valor inválido para o flip vertical, o flip deve ser 1 ou 0")
        
        self._send_command_to_espCam("vflip", val)

    def get_frame(self):
        """
        Retorna o frame mais atual obtido pela ESP32-CAM
        """
        with self.lock:
            return self.frame

    def get_frame_time(self):
        """
        Retorna o momento em que o frama mais recente foi obtido
        """
        with self.lock:
            return self.frame_time

    def isRunning(self) -> bool:
        """
        Retorna o estado da camera
        """
        return self.starded

    def cleanup(self):
        """
        Limpa todos os recursos, fecha as janelas existentes e libera o hardware
        """
        self.stop_stream()
        cv2.destroyAllWindows()