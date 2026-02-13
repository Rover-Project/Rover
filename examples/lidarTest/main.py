import serial 
import time 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

x_axisData = [] # informacoes para o eixo x (frames)
dist_data = [] # dados da distancia
strength_data = [] # dados da forca do sinal
temp_data = [] # dados da temperatura

MAX_POINTS_GRAPH = 50 # numero maximo de pontos no grafico

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
                
                # print(f"Distância: {distance}cm | Força: {strength} | Temp: {temperature:.2f}°C")
                return distance, strength, temperature
    return None

def updateGraph(data):
    data = getLidarData()

    if data:
        dist, stren, temp = data

        x_axisData.append(len(x_axisData))
        dist_data.append(dist)
        strength_data.append(stren)
        temp_data.append(temp)

        if len(x_axisData) > MAX_POINTS_GRAPH:
            x_axisData.pop(0)
            dist_data.pop(0)
            strength_data.pop(0)
            temp_data.pop(0)

        dist_line.set_data(range(len(dist_data)), dist_data)
        strengh_line.set_data(range(len(strength_data)), strength_data)
        temp_line.set_data(range(len(temp_data)), temp_data)

        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
        ax2_temp.relim()
        ax2_temp.autoscale_view()

    return dist_line, strengh_line, temp_line
    
if __name__ == "__main__":

    # Graph config
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(hspace=0.4)

    if fig and ax1 and ax2:

        # Distance graph
        dist_line, = ax1.plot([], [], '-r', label='Distância (cm)')
        ax1.set_ylabel('cm')
        ax1.set_title('Leitura em Tempo Real - TF LUNA')
        ax1.legend(loc='upper right')
        ax1.grid(True)

        strengh_line, = ax2.plot([], [], '-b', label='Strenght')
        ax2_temp = ax2.twinx() # Segundo eixo y para a temperatura
        temp_line, = ax2_temp.plot([], [], '-g', label="Temp (ºC)")
        ax2.set_ylabel("Forca")
        ax2_temp.set_ylabel("Temp (ºC)")
        ax2.legend(loc="upper left")
        ax2_temp.legend(loc="upper right")
        ax2.grid(True)

        ani = FuncAnimation(fig, updateGraph, interval=10, cache_frame_data=False)

        plt.show()
        uart_lidar.close()

