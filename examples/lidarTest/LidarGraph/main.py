from roverlib.plugins.lidar.exceptions import LidarNotStart#type: ignore
from roverlib.plugins.lidar.lidar import Lidar #type: ignore
import serial #type: ignore
import matplotlib.pyplot as plt #type: ignore
from matplotlib.animation import FuncAnimation #type: ignore
import time

x_axisData = [] # informacoes para o eixo x (frames)
dist_data = [] # dados da distancia
strength_data = [] # dados da forca do sinal
temp_data = [] # dados da temperatura

MAX_POINTS_GRAPH = 50 # numero maximo de pontos no grafico

lidar = Lidar()
try:
    lidar.start()
except Exception as e:
    print(f"Falha ao iniciar: {e}")
    raise LidarNotStart("O Lidar não iniciou")

def updateGraph(frame):
    latest_data = None

    try:
        latest_data = lidar.get_read()
        print(f"Latest_data: {latest_data}")

        # Só processamos dist, stren e temp se latest_data existir
        if latest_data:
            dist, stren, temp = latest_data

            x_axisData.append(len(x_axisData))
            dist_data.append(dist)
            strength_data.append(stren)
            temp_data.append(temp)

            if len(x_axisData) > MAX_POINTS_GRAPH:
                x_axisData.pop(0)
                dist_data.pop(0)
                strength_data.pop(0)
                temp_data.pop(0)
        
    except Exception as e:
        print(f"Erro: {e}")

    dist_line.set_data(range(len(dist_data)), dist_data)
    strengh_line.set_data(range(len(strength_data)), strength_data)
    temp_line.set_data(range(len(temp_data)), temp_data)

    ax1.set_xlim(0, MAX_POINTS_GRAPH)
    ax2.set_xlim(0, MAX_POINTS_GRAPH)

    return dist_line, strengh_line, temp_line
    
# PARTE EXECUTAVEL
try:
    # Graph config
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(hspace=0.4)
    fig.canvas.manager.set_window_title("Monitor TF-Luna") 

    if fig and ax1 and ax2:

        # Distance graph
        dist_line, = ax1.plot([], [], '-r', label='Distância (cm)')
        ax1.set_ylim(0, 800) # 8 metros = 800 cm
        ax1.set_ylabel('cm')
        ax1.set_title('Leitura em Tempo Real - TF LUNA')
        ax1.legend(loc='upper right')
        ax1.grid(True)

        # Grafico para forca e temperatura
        strengh_line, = ax2.plot([], [], '-b', label='Strenght')
        ax2_temp = ax2.twinx() # Segundo eixo y para a temperatura
        temp_line, = ax2_temp.plot([], [], '-g', label="Temp (ºC)")

        ax2.set_ylim(0, 4000)    
        ax2.set_ylabel("Forca")
        
        ax2_temp.set_ylim(-10, 50)
        ax2_temp.set_ylabel("Temp (ºC)")

        ax2.legend(loc="upper left")
        ax2_temp.legend(loc="upper right")
        ax2.grid(True)

        ani = FuncAnimation(fig, updateGraph, interval=30, cache_frame_data=False)

        plt.show()
        lidar.stop()

except KeyboardInterrupt or Exception as e:
    print("Deu errado ou foi interrompido")
