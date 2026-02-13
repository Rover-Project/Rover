import serial 
import time 

try:
    uart_lidar = serial.Serial(
        port='/dev/ttyAMA0', # Valor para os pinos fisicos 14 (TX) e 15 (RX)
        baudrate=115200, # Velocidade de transmissao padrao do TF-LUNA
        parity=serial.PARITY_NONE, # Sem bit de paridade (Sem verificacao de erro simples)
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
except Exception as e:
    print(f"Erro ao acessar os pinos TX/RX: {e}")
    exit()

def getLidarData(serial_in):
    # O pacote do TF-Luna tem 9 bytes
    if uart_lidar.in_waiting >= 9:
        # Sincronização: Lemos até achar o primeiro 0x59
        byte1 = uart_lidar.read(1)
        if byte1 == b'\x59':
            byte2 = uart_lidar.read(1)
            if byte2 == b'\x59':
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
    try:
        while True:
            getLidarData(uart_lidar)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nEncerrando...")
        uart_lidar.close()

