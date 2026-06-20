from roverlib.modules.processing.processing_image import ProcessingImage
from .exceptions import EspCamNotStart, EspCamNotRespond, NotUsableValues
from .cameraInterface import CameraInterface
from time import time, sleep
import requests
import cv2
import threading

class EspCamera(CameraInterface):
    """
    Plugin feito para controle de ações realizadas pela Esp32 Cam.
    """

    def __init__(self, esp_ip: str):
        """
        Realiza a configuração inicial da câmera.
        """    
        self.ip = esp_ip
        self.url_stream = f"http://{esp_ip}:81/stream"
        self.url_control = f"http://{esp_ip}/control"

        self.capture = None
        self.started = False
        self.thread = None

        # Variáveis para estado do frame capturado
        self.frame = None
        self.frame_time = 0.0
        self.lock = threading.Lock()

    def _send_command_to_espCam(self, var: str, valor):
        """Envia uma requisição HTTP para a esp32 Cam com objetivo de 
        alterar seus parâmetros em tempo de execução
        """
        parametros = {'var': var, 'val': valor}
        try:
            # http://192.168.4.1/control?var= ****** &val= ******
            answer = requests.get(self.url_control, params=parametros, timeout=1)
            if answer.status_code == 200:
                print(f"Sucesso: {var} alterado para {valor}")
            else: 
                print(f"Erro na ESP32: Status {answer.staus_code}")
        except EspCamNotStart as e:
            print(e)
            return False

    def start_stream(self):
        """
        Inicia a captura da câmera em outra thread
        """

        if self.started:
            print("ESP32-CAM já está rodando!")
            return True
        
        print("Conectando ao streamimng...")
        self.capture = cv2.VideoCapture(self.stream_url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) # minimiza o tamanho do Buffer para mais perfomance

        if not self.capture.isOpened():
            raise EspCamNotStart
        
        self.started = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        print("ESP32-CAM iniciada corretamente!")
        return True
    
    def _update(self):
        """
        Método interno de leitura continua executado pela Thread 
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
                return

    def stop_stream(self):
        """
        Para temporareamente a leitura do stream
        """
        if not self.started:
            return 
        
        self.starded = False
        if self.thread is not None:
            self.thread.join(timeout=2) # aguarda a thread finalizar com segurança
        
        if self.capture is not None:
            self.capture.release()

        print("STREAM INTERROMPIDO")
        return

    def quality(self, val: int):
        """
        Ajusta a qualidade da imagem captura
        Args: 
            val (int): Um valor entre 10 e 63, que quanto menor, mais qualidade tem a imagem
        """

        if val < 10 or val > 63: 
            raise NotUsableValues
        
        self._send_command_to_espCam("quality", val)
        return

    def set_brightness(self, val: int):
        """
        Ajusta o o brilho da Esp Cam
        Args:
            val (int): Valor entre -2 e 2
        """

        if val < 2 or val > 2: 
            raise NotUsableValues
        
        self._send_command_to_espCam("brightness", val)
        return
    
    def set_contast(self, val: int):
        """
        Ajusta o contraste da Esp Cam
        Args:
            val (int): Valor entre -2 e 2
        """

        if val > 2 or val < -2:
            raise ValueError
        
        self._send_command_to_espCam("contrast", val)
        print("Contraste alterado com sucesso")
        return

    def set_saturation(self, val: int):
        """
        Ajusta a saturação da Esp Cam
        Args:
            val (int): Valor entre -2 e 2
        """

        if val > 2 or val < -2:
            raise ValueError
        
        self._send_command_to_espCam("saturation", val)
        print("Saturação alterada com sucesso")
        return


    def set_white_balance(self, val: int):
        """
        Ativa ou desativa o balanço de branco automático da Câmera
        Args:
            val (int): 1 para ativado, 0 para desativado
        """
        if val < 0 or val > 1:
            raise ValueError
        self._send_command_to_espCam("awb", val)
        print("Modo de balanço de brancos automático alterado!")
        return

    def set_mode_of_awb(self, val: int):
        """
        Altera o tipo de balanço de branco automátic
        Args: 
            val (int):      
                - 0: Auto;
                - 1: Ensolarado;
                - 2: Nublado;
                - 3: Fluorescente;
                - 4: Incandescente.
        """
        
        if val < 0 or val > 4:
            raise ValueError
        
        self._send_command_to_espCam("awb", 1) # Os modos só podem ser alterados se awb estiver ON
        self._send_command_to_espCam("wb_mode", val)

        print("Modo de balanço de branco alterado")
        return

    def set_auto_exposition(self, val: int):
        """
        Ativa ou desativa o modo de controle de exposição automática.
        Args:
            val (int): 1 para ATIVADO, 0 para DESATIVADO
        """
        if val < 0 or val > 1:
            raise ValueError
        
        self._send_command_to_espCam("aec", val)
        return
    # --- EXISTEM DIVERSOS OUTRAS OPÇÕES QUE PODEM VALER SEREM EXPLORADAS FUTURAMENTE. ---

    def set_framesize(self, val: int):
        """
        Altera a proporção da imagem capturada
        Arg:
            val (int): 
            - 4: (640 X 480)
            - 5: (400 X 296)
            - 6: (320 X 240)
            - 7: (240 X 240)
            - 8: (800 X 600)
            - 9: (1024 X 768)
            - 10: (1280 X 1024)
            - 11: (1600 X 1200)
        """

        if val < 4 or val > 11:
            raise NotUsableValues
        
        self._send_command_to_espCam("framesize", val)
        print("Proporção da imagem altera com sucesso!")
        return

    def h_mirroring(self, val: int):
        """
        Espelha a imagem horizontalmente
        Args:
            val (int): 0 para orientação padrão, 1 para invertida
        """
        if val < 0 or val > 1:
            raise NotUsableValues

        self._send_command_to_espCam("hmirror", val)
        print("Imagem invertida horizontalmente!")
        return 

    def v_flip(self, val: int):
        """
        "Espelha" a imagem verticalmente.
        Args:
            val (int): 0 para orientação padrão, 1 para invertida
        """

        if val < 0 or val > 1:
            raise NotUsableValues
        
        self._send_command_to_espCam("vflip", val)
        print("Imagem invertida verticalmente")
        return

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
        return self.starded

    def cleanup(self):
        """
        Limpa todos os recursos, fecha as janelas existentes e libera o hardware
        """
        self.stop_stream()
        cv2.destroyAllWindows()
        print("ESP32-CAM: Recursos limpos e liberados")
        return