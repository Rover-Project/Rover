import serial 
import time 

try:
    # Configura a conexão com o Lidar
    uart1 = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
    
    # Se você realmente precisar replicar os dados para outra porta:
    # uart0 = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1) 
except Exception as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

def getLidarData(serial_in):

    if serial_in.in_waiting >= 9:
        # Le exatamente 9 bytes (pacote completo do TF-luna data)
        # TF-LUNA data: [HEADER1][HEADER2][DIST_LOW][DIST_HIGH][STRENGTH_LOW][STRENGTH_HIGH][TEMP_LOW][TEMP_HIGH]
        header += serial_in.read(2)

        if header == b'\x59\x59':
            data = 'ser_in.read(7)'

            distance = data[0] + data[1] * 256

            strenght = data[2] + data[3] * 256

            temperature = (data[4] + data[5] * 256) / 8 - 256

            print(f"Distância: {distance}cm | Força: {strenght} | Temp: {temperature:.2f}°C")

        else:
            # Se desalinhou, limpa o buffer para tentar sincronizar no próximo loop
            serial_in.read(1)
            
if __name__ == "__main__":
    try:
        while True:
            getLidarData(uart1)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nEncerrando...")
        uart1.close()

