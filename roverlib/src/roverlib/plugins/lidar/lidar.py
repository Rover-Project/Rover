import serial

try:
    from serial import Timeout
    availableLidar = True
except (ImportError, ModuleNotFoundError):
    availableLidar = False

class Lidar():
    """
    Plugin do Lidar TF-Luna. Realiza sua configuração e controle
    """

    def __init__(
        self, 
        port, # '/dev/ttyAMA0'
        baudrate:int = 115200,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout: int = 1
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

        if not availableLidar:
            raise ModuleNotFoundError("Não foi possível importar o modulo Serial")
        
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.lidar = None

    def start(self):
        """
        Inicia o funcionamento do Lidar com as configurações estabelecidas
        """
        lidar = serial.Serial(
            self.port, self.baudrate,
            self.parity, self.stopbits,
            self.bytesize, self.timeout
        )
        self.lidar = lidar
        return lidar
    
    def kill(self):
        """
        Encerra a operação do Lidar
        """
        ul_state = self.lidar.is_open()

        if ul_state:
            self.lidar.reset_input_buffer()
            self.lidar.reset_output_buffer()
            self.lidar.close()
        
        else: 
            print("A porta já está fechada")
    
    def change_config(self):
        """
        Permite mudança nas configurações do Lidar e retorna um dict com essas
        """
        config = self.lidar.get_settings()
        print(config)

        self.lidar.apply_settings(config)
        return config

    def clean_buffer(self):
        """
        Limpa os buffers de entrada e saída do Lidar
        """
        self.lidar.reset_input_buffer()
        self.lidar.reset_output_buffer()

    def status(self):
        """
        Exibe e retorna o status, quantidade de bits no buffer de entrada
        e quantidade de bits no buffer de saida do Lidar
        """
        state = self.lidar.is_open()        
        in_buffer = self.lidar.in_waiting()
        out_buffer = self.lidar.out_waiting()

        return state, in_buffer, out_buffer

    def get_reads(self, quant:int):
        """
        Retorna o número de bytes passado como arg
        
        args:
        quant = Quantidade de bytes esperados para encerrar a leitura
        """
        reads = self.lidar.read_until(b"\n", quant)
        return reads
    
