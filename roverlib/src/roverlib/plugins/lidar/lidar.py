from .exceptions import LidarNotStart, LidarDoNotRespond
from threading import Thread
import time
try:
    import serial # type: ignore
    availableSerial = True
except (ImportError, ModuleNotFoundError):
    availableSerial = False

class Lidar():
    """
    Plugin do Lidar TF-Luna. Realiza sua configuração e controle
    """

    def __init__(
        self, 
        # Ordem a ser passada para a função .serial()
        port: str = '/dev/ttyAMA0', # 1º
        baudrate: int = 115200, # 2º
        bytesize = serial.EIGHTBITS, # 3º 
        parity = serial.PARITY_NONE, # 4º
        stopbits = serial.STOPBITS_ONE, # 5º
        timeout: int = 1 # 6º
    ):
        """
        Realiza a configuração inicial do Lidar.

        Args:
            port = recebe o arquivo de dispositivo com os pinos da GPIO
            baudrate = Define a velocidade do sinal. Ambos os dispositivos devem trabalhar na mesma velocidade
            parity = Não adiciona bit de paridade
            stopbits = Um bit de duração lógica alta ao final de cada pacote
            bytesize = Tamanho de cada pacote
            timeout = Tempo máximo de espera pelo próximo pacote (segundos)
        """

        if not availableSerial:
            raise ModuleNotFoundError("Não foi possível importar o modulo serial")
        
        self.port = port # Portas onde o Lidar foi conectado
        self.baudrate = baudrate # Frequencia de operacao
        self.bytesize = bytesize # Tamanho da informacao transmitida
        self.parity = parity # Estado do bit de paridade
        self.stopbits = stopbits # Quantidade de stopbits para cada pacote
        self.timeout = timeout # Intervalo entre cada leitura 
        self.lidar = None # Objeto do Lidar
        self.max_buffer_reads = 517 # threshold para a quantidade de leituras armazenadas no buffer
        self.distance = -1
        self.strenght = -1
        self.temperature = -1
        self.is_read_running = False
        self._thread = None

    def start(self):
        """
        Inicia o funcionamento do Lidar com as configurações estabelecidas
        """
        try:
            lidar = serial.Serial(
                self.port, 
                self.baudrate,
                self.bytesize,
                self.parity, 
                self.stopbits, 
                self.timeout
            )

            state = lidar.is_open

            if not state:
                raise LidarNotStart("Não foi possivel iniciar o Lidar. Verifique as conexões")
            
            else:
                self.lidar = lidar
                self.is_read_running = True
                self._thread = Thread(target=self._update_data, daemon=True)
                self._thread.start()
                print("lidar iniciado e leitura rolando")
            
        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")
    
    def is_open(self):
        """
        Verifica o estado do Lidar
        
        Retorna:
            Valor Bool: (True se ativo, false se nao)
        """
        return self.lidar.is_open
    
    def _update_data(self):
        """
        Realiza as leituras e atualiza as variaveis de distancia, forca do sinal
        E temperatura com as informacoes vindas do Lidar
        
        Raises:
            LidarNotStart: RunTimeError pois o Lidar não foi iniciado corretamente
            LidarNotRespond: O Lidar foi iniciado, mas não envia nenhum dado
        """

        # Raises podem nao aparecer no terminal vindo de threads
        if not self.is_open():
            print("O lidar nao foi iniciado")
            return

        while self.is_read_running:

            if self.get_in_buffer() > self.max_buffer_reads:
                self.clean_in_buffer()
            
            data = self.lidar.read(9)
            
            if self.lidar.in_waiting >= 9:
                print("Leitura realizada mas não casou com o cabeçalho")
                if data[0] == b'\x59' and data[1] == b'\x59':
                
                    # Distância: Byte 2 e 3 (índices 0 e 1 do data)
                    self.distance = data[2] + data[3] * 256
                    
                    # Força do sinal: Byte 4 e 5 (índices 2 e 3 do data)
                    self.strenght = data[4] + data[5] * 256
        
                    # Temperatura: Byte 6 e 7 (índices 4 e 5 do data)
                    temp_raw = data[6] + data[7] * 256
                    self.temperature = temp_raw / 8 - 256
                
            else:
                print("Não foi possível realizar leitura")
            time.sleep(0.01)


    def get_read(self):
        """
        Getter das leituras do Lidar

        Retorna:
            Distância da superfície, força do sinal e temperatura do chip
            Nessa ordem
        """
        
        return self.distance, self.strenght, self.temperature
        
    def stop(self):
        """
        Encerra a operação do Lidar
        """
        if self.is_open():
            self.lidar.reset_input_buffer()
            self.lidar.reset_output_buffer()
            self.lidar.close()

            self.is_read_running = False
            if self._thread:
                self._thread.join()
        
    def change_config(self):
        """
        Permite mudança nas configurações do Lidar e retorna um dict com essas
        """
        try:
            if self.is_open():
                config = self.lidar.get_settings()
                self.lidar.apply_settings(config)
                
                return config
            
        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")

    def clean_in_buffer(self):
        """
        Limpa o buffer de entrada do lidar

        Raise:
            LidarNotStart: Para evitar comportamento inesperado, caso tente limpar o que não existe
        """
        if self.is_open():
            self.lidar.reset_input_buffer()

    def clean_out_buffer(self):
        """
        Limpa o buffer de entrada do lidar

        Raise:
            LidarNotStart: Para evitar comportamento inesperado, caso tente limpar o que não existe
        """
        if self.is_open():
            self.lidar.reset_output_buffer()

    def get_in_buffer(self):
        """
        Adquire a quantidade de bytes no buffer de entrada do lidar

        Retorna:
            in_buffer: Quantidade de bytes no buffer de entrada
        """

        if self.is_open():
            in_buffer = self.lidar.in_waiting
            return in_buffer
        
    def get_out_buffer(self):
        """
        Adquire a quantidade de bytes no buffer de saida do lidar

        Retorna:
            out_buffer: Quantidade de bytes no buffer de saida
        """

        if self.is_open():
            out_buffer = self.lidar.out_waiting
            return out_buffer
    
    def get_reads_until(self, quant:int):
        """
        Realiza uma leitura continua que se encerra
        de acordo com o número de bytes desejado

        args:
            quant = Quantidade de bytes esperados para encerrar a leitura

        Retorna:
            Os bytes lidos até satisfeita a quantidade desejada

        Raises:
            LidarNotStart: RunTimeError pois o Lidar não foi iniciado corretamente
            LidarNotRespond: O Lidar foi iniciado, mas não envia nenhum dado
        """
            
        if self.is_open():
            answer = self.lidar.read(5)
            if not answer:
                raise LidarDoNotRespond("O lidar não está retornando nada")
            
            else:

                reads = self.lidar.read_until(b"\n", quant)
                return reads