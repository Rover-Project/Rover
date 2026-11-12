from .exceptions import LidarNotStart, LidarDoNotRespond
from threading import Thread, current_thread
import time
try:
    import serial # type: ignore
    availableSerial = True
except (ImportError, ModuleNotFoundError):
    serial = None
    availableSerial = False

# Constantes do quadro UART do TF-Luna (9 bytes: 0x59 0x59 Dist_L Dist_H Str_L Str_H Temp_L Temp_H Checksum)
_FRAME_HEADER = 0x59
_FRAME_SIZE = 9

# Segundo o datasheet do TF-Luna, a distância não é confiável
# quando a força do sinal é menor que 100 ou igual a 65535 (saturação)
_MIN_STRENGTH = 100
_SATURATED_STRENGTH = 65535

# Temperatura do chip a partir da qual o Lidar é desligado por segurança
_MAX_TEMPERATURE = 65.0


class Lidar():
    """
    Plugin do Lidar TF-Luna. Realiza sua configuração e controle.

    O TF-Luna mede a distância de um único ponto (à frente do sensor),
    entre 0,2 m e 8 m.

    Exemplo:
        with Lidar() as lidar:
            print(lidar.get_distance())
            if lidar.is_obstacle(30):
                print("Obstáculo a menos de 30 cm!")
    """

    def __init__(
        self,
        # Ordem a ser passada para a função .serial()
        port: str = '/dev/ttyAMA0', # 1º
        baudrate: int = 115200, # 2º
        bytesize: int = 8, # 3º  (serial.EIGHTBITS)
        parity: str = 'N', # 4º  (serial.PARITY_NONE)
        stopbits: float = 1, # 5º  (serial.STOPBITS_ONE)
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
            raise ModuleNotFoundError("Não foi possível importar o modulo serial. Instale com: pip install pyserial")

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
        self._last_read = (-1, -1, -1) # Última leitura completa (atribuída de uma vez, para não misturar quadros)
        self.is_read_running = False
        self._thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
        return False

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
        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")

        if not lidar.is_open:
            raise LidarNotStart("Não foi possivel iniciar o Lidar. Verifique as conexões")

        self.lidar = lidar
        self.is_read_running = True
        self._thread = Thread(target=self._update_data, daemon=True)
        self._thread.start()
        print("lidar iniciado e leitura rolando")

    def is_open(self):
        """
        Verifica o estado do Lidar

        Retorna:
            Valor Bool: (True se ativo, false se nao)
        """
        return self.lidar is not None and self.lidar.is_open

    def _update_data(self):
        """
        Laço executado em segundo plano que lê e decodifica os quadros do TF-Luna.
        """
        if not self.is_open():
            print("O lidar nao foi iniciado")
            return

        try:
            while self.is_read_running:
                waiting = self.lidar.in_waiting

                # Se o buffer acumulou muitos dados antigos, descarta para manter o tempo real
                if waiting > self.max_buffer_reads:
                    self.lidar.reset_input_buffer()
                    continue

                # Verifica se há bytes suficientes ANTES de ler
                if waiting < _FRAME_SIZE:
                    time.sleep(0.005)
                    continue

                # Procura pelo cabeçalho 0x59 0x59 para sincronizar o frame
                # Isso evita ler dados "quebrados" ou deslocados
                if self.lidar.read(1) != bytes([_FRAME_HEADER]):
                    continue
                if self.lidar.read(1) != bytes([_FRAME_HEADER]):
                    continue

                # Se achou os dois 0x59, lê os próximos 7 bytes
                data = self.lidar.read(_FRAME_SIZE - 2)
                if len(data) < _FRAME_SIZE - 2:
                    continue # Backup caso a leitura falhe no meio

                # Checksum: byte menos significativo da soma dos 8 primeiros bytes
                if (2 * _FRAME_HEADER + sum(data[:6])) & 0xFF != data[6]:
                    continue # Quadro corrompido, descarta

                # Distância (Bytes 2 e 3 do frame total)
                distance = data[0] + (data[1] << 8)
                # Força do sinal (Bytes 4 e 5)
                strength = data[2] + (data[3] << 8)
                # Temperatura (Bytes 6 e 7)
                temperature = (data[4] + (data[5] << 8)) / 8 - 256

                self._last_read = (distance, strength, temperature)
                self.distance, self.strenght, self.temperature = self._last_read

                if temperature > _MAX_TEMPERATURE:
                    print(f"Temperatura Crítica: {temperature}°C! Encerrando...")
                    self.stop()
                    break
        except (serial.SerialException, OSError, TypeError, AttributeError):
            # A porta foi fechada durante a leitura (ex.: stop() chamado em outra thread)
            if self.is_read_running:
                raise

    def get_read(self):
        """
        Getter das leituras do Lidar

        Retorna:
            Distância da superfície (cm), força do sinal e temperatura do chip (°C)
            Nessa ordem. Retorna (-1, -1, -1) enquanto nenhuma leitura foi feita.
        """
        return self._last_read

    def get_distance(self, unit: str = "cm"):
        """
        Retorna apenas a distância medida pelo Lidar.

        Args:
            unit = Unidade da distância: "cm" (padrão), "m" ou "mm"

        Retorna:
            A distância na unidade escolhida, ou None se ainda não houver leitura
            ou se a leitura não for confiável (sinal fraco ou saturado).
        """
        factors = {"cm": 1, "m": 0.01, "mm": 10}
        if unit not in factors:
            raise ValueError(f"Unidade inválida '{unit}'. Use 'cm', 'm' ou 'mm'.")

        distance, strength, _ = self._last_read
        if distance < 0 or strength < _MIN_STRENGTH or strength == _SATURATED_STRENGTH:
            return None

        return distance * factors[unit]

    def is_obstacle(self, limit_cm: float = 30) -> bool:
        """
        Indica se existe um obstáculo à frente, mais perto que o limite.

        Args:
            limit_cm = Distância limite em centímetros (padrão: 30 cm)

        Retorna:
            True se houver uma leitura válida menor ou igual ao limite, False caso contrário.
        """
        distance = self.get_distance("cm")
        return distance is not None and distance <= limit_cm

    def stop(self):
        """
        Encerra a operação do Lidar.
        Pode ser chamado mais de uma vez e também de dentro da thread de leitura.
        """
        # Sinaliza a thread ANTES de fechar a porta, para ela não ler de uma porta fechada
        self.is_read_running = False

        if self._thread and self._thread.is_alive() and self._thread is not current_thread():
            self._thread.join(timeout=1)

        if self.is_open():
            self.lidar.reset_input_buffer()
            self.lidar.reset_output_buffer()
            self.lidar.close()

    def change_config(self, **settings):
        """
        Permite mudança nas configurações da porta serial do Lidar.

        Args:
            **settings = Configurações a alterar (ex.: timeout=2, baudrate=115200).
                         Sem argumentos, apenas retorna as configurações atuais.

        Retorna:
            dict com as configurações atuais (após a alteração)
        """
        if not self.is_open():
            raise LidarNotStart("O Lidar não foi iniciado")

        try:
            config = self.lidar.get_settings()
            invalid = set(settings) - set(config)
            if invalid:
                raise ValueError(f"Configurações inválidas: {', '.join(sorted(invalid))}")

            config.update(settings)
            self.lidar.apply_settings(config)
            return self.lidar.get_settings()

        except serial.SerialException as e:
            raise LidarNotStart(f"Houve algum tipo de falha física {e}")

    def clean_in_buffer(self):
        """
        Limpa o buffer de entrada do lidar
        """
        if self.is_open():
            self.lidar.reset_input_buffer()

    def clean_out_buffer(self):
        """
        Limpa o buffer de saída do lidar
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
            return self.lidar.in_waiting

    def get_out_buffer(self):
        """
        Adquire a quantidade de bytes no buffer de saida do lidar

        Retorna:
            out_buffer: Quantidade de bytes no buffer de saida
        """
        if self.is_open():
            return self.lidar.out_waiting

    def get_reads_until(self, quant: int):
        """
        Lê bytes brutos da porta serial até atingir a quantidade desejada
        (ou até o timeout). Uso avançado/depuração: enquanto a leitura em
        segundo plano estiver ativa, ela também consome os bytes da porta.

        args:
            quant = Quantidade de bytes esperados para encerrar a leitura

        Retorna:
            Os bytes lidos até satisfeita a quantidade desejada

        Raises:
            LidarNotStart: RunTimeError pois o Lidar não foi iniciado corretamente
            LidarNotRespond: O Lidar foi iniciado, mas não envia nenhum dado
        """
        if not self.is_open():
            raise LidarNotStart("O Lidar não foi iniciado")

        reads = self.lidar.read(quant)
        if not reads:
            raise LidarDoNotRespond("O lidar não está retornando nada")

        return reads
