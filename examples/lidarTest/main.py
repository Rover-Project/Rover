import serial 
import time 

try:
    uart_lidar = serial.Serial(
        port='/dev/ttyAMA0', # Valor para os pinos fisicos 14 (TX) e 15 (RX)
        baudrate=115200, # Velocidade de transmissao padrao do TF-LUNA
        parity=serial.PARITY_NONE, # Sem bit de paridade (Sem verificacao de erro simples)
        stopbits=serial.STOPBITS_ONE, # Configuracao que garante uma pausa entre cada informacao recebida antes do proximo byte
        bytesize=serial.EIGHTBITS, # quantidade de informacao util em cada pacote
        timeout=1 # Se nao recebere nada em 1 segundo, para o aguardo
    )
# Except para caso as portas estejam ocupadas ou nao existam
except Exception as e:
    print(f"Erro ao acessar os pinos TX/RX: {e}")
    exit()

def getLidarData():
    # O pacote do TF-Luna tem 9 bytes
    # .in_waiting verifica quantos bytes estam no buffer vindo do lidar
    if uart_lidar.in_waiting >= 9:

        # Le byte por byte ate encontrar o inicio do pacote
        byte1 = uart_lidar.read(1)
        if byte1 == b'\x59': # primeiro Header
            byte2 = uart_lidar.read(1)
            if byte2 == b'\x59': # segundo Header
                # Se achou 0x59 0x59, lê os próximos 7 bytes
                payload = uart_lidar.read(7)
                
                # Distância: Byte 2 e 3 (índices 0 e 1 do payload)
                distance = payload[0] + payload[1] * 256
                
                # Força do sinal: Byte 4 e 5 (índices 2 e 3 do payload)
                strength = payload[2] + payload[3] * 256
                
                # Temperatura: Byte 6 e 7 (índices 4 e 5 do payload)
                temp_raw = payload[4] + payload[5] * 256
                temperature = temp_raw / 8 - 256
                
                print(f"Distância: {distance}cm | Força: {strength} | Temp: {temperature:.2f}°C")
                return distance, strength, temperature
    return None
    
if __name__ == "__main__":

    while True:
        try:
            getLidarData()
            time.sleep(0.01)
        except KeyboardInterrupt as e:
            print('Não deu certo ou foi interrompido')
            break