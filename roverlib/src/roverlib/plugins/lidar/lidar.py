import serial
from .exceptions import LidarNotStart
from .exceptions import LidarDoNotRespond
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
        port = '/dev/ttyAMA0', # '/dev/ttyAMA0 => padrao para componentes atuais'
        baudrate :int = 115200,
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
        try:
            lidar = serial.Serial(
                self.port, self.baudrate,
                self.parity, self.stopbits,
                self.bytesize, self.timeout
            )

            state = lidar.is_open()

            if not state:
                raise LidarNotStart("Nao foi possivel iniciar o Lidar. Verifique as conexoes")
            
            else:
                self.lidar = lidar
                return self.lidar
            
        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")

    def kill(self):
        """
        Encerra a operação do Lidar
        """
        state = self.lidar.is_open()

        if state:
            self.lidar.reset_input_buffer()
            self.lidar.reset_output_buffer()
            self.lidar.close()
        
        else: 
            print("A porta já está fechada")
    
    def change_config(self):
        """
        Permite mudança nas configurações do Lidar e retorna um dict com essas
        """
        try:
            state = self.lidar.is_open()

            if not state:
                raise LidarNotStart("O Lidar nao foi iniciado")
            
            else:
                config = self.lidar.get_settings()
                print(config)

                self.lidar.apply_settings(config)
                return config
            
        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")

    def clean_buffer(self):
        """
        Limpa os buffers de entrada e saída do Lidar

        Raise:
            LidarNotStart: Para evitar comportamento inesperado, caso tente limpar o que nao existe
        """

        state = self.lidar.is_open()

        if not state:
            raise LidarNotStart("O lidar nao foi iniciado")
        else:
            self.lidar.reset_input_buffer()
            self.lidar.reset_output_buffer()

    def get_buffers(self):
        """
        Adquire a quantidade de bytes no buffer de entrada
        e de saida do Lidar

        Retorna:
            (in_buffer, out_buffer) Tupla com valores int da quantidade de bytes nos dois buffers
        """
        in_buffer = self.lidar.in_waiting()
        out_buffer = self.lidar.out_waiting()

        return in_buffer, out_buffer

    def is_open(self):
        """
        Verifica o estado do Lidar
        
        Retorna:
            Valor Bool: (True se ativo, false se nao)
        """
        state = self.lidar.is_open()
        return state

    def get_read(self):
        """
        Realiza uma leitura simples dos dados adquiridos pelo Lidar
        (Leitura simples = 9 bytes, que representam um pacote completo)

        Retorna:
            Distância da superfície, força do sinal e temperatura do chip
            Nessa ordem

        Raises:
            LidarNotStart: RunTimeError pois o Lidar não foi iniciado corretamente
            LidarNotRespond: O Lidar foi iniciado, mas não envia nenhum dado
        """
        state = self.lidar.is_open()
        
        if not state:
            raise LidarNotStart("O lidar nao foi iniciado")
            
        else:
            answer = self.lidar.read(5)
            if not answer:
                raise LidarDoNotRespond("O lidar não está retornando nada")
            
            else:

                if self.lidar.in_waiting() >= 9:

                    # Le byte por byte ate encontrar o inicio do pacote
                    byte1 = self.lidar.read(1)
                    if byte1 == b'\x59': # primeiro Header
                        byte2 = self.lidar.read(1)
                        if byte2 == b'\x59': # segundo Header
                            # Se achou 0x59 0x59, lê os próximos 7 bytes
                            payload = self.lidar.read(7)
                            
                            # Distância: Byte 2 e 3 (índices 0 e 1 do payload)
                            distance = payload[0] + payload[1] * 256
                            
                            # Força do sinal: Byte 4 e 5 (índices 2 e 3 do payload)
                            strength = payload[2] + payload[3] * 256
                            
                            # Temperatura: Byte 6 e 7 (índices 4 e 5 do payload)
                            temp_raw = payload[4] + payload[5] * 256
                            temperature = temp_raw / 8 - 256
                            
                            print(f"Distância: {distance}cm | Força: {strength} | Temp: {temperature:.2f}°C")
                            return distance, strength, temperature
    
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
        state = self.lidar.is_open()
        
        if not state:
            raise LidarNotStart("O lidar nao foi iniciado")
            
        else:
            answer = self.lidar.read(5)
            if not answer:
                raise LidarDoNotRespond("O lidar não está retornando nada")
            
            else:

                reads = self.lidar.read_until(b"\n", quant)
                return reads