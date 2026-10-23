import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from roverlib.plugins.lidar.lidar import Lidar
from roverlib.plugins.lidar.exceptions import LidarNotStart
from roverlib.utils.config_manager import Config
from pathlib import Path

class LidarMonitorApp:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        graph_config = self.config.get("graph", {"max_points": 50, "interval_ms": 30})
        
        self.max_points = graph_config["max_points"]
        self.interval_ms = graph_config["interval_ms"]
        
        self.x_data = []
        self.dist_data = []
        self.strength_data = []
        self.temp_data = []

        self.lidar = Lidar()
        try:
            self.lidar.start()
        except Exception as e:
            print(f"Falha ao iniciar o Lidar: {e}")
            raise LidarNotStart("O Lidar não iniciou")

        self._setup_graph()

    def _setup_graph(self):
        """Configura a interface do Matplotlib."""
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        plt.subplots_adjust(hspace=0.4)
        self.fig.canvas.manager.set_window_title("Monitor TF-Luna")

        # Gráfico de Distância
        self.dist_line, = self.ax1.plot([], [], '-r', label='Distância (cm)')
        self.ax1.set_ylim(0, 800) # 8 metros = 800 cm
        self.ax1.set_ylabel('cm')
        self.ax1.set_title('Leitura em Tempo Real - TF LUNA')
        self.ax1.legend(loc='upper right')
        self.ax1.grid(True)

        # Gráfico de Força e Temperatura
        self.strengh_line, = self.ax2.plot([], [], '-b', label='Strength')
        self.ax2_temp = self.ax2.twinx()
        self.temp_line, = self.ax2_temp.plot([], [], '-g', label="Temp (ºC)")

        self.ax2.set_ylim(0, 8000)
        self.ax2.set_ylabel("Força")
        self.ax2_temp.set_ylim(-10, 50)
        self.ax2_temp.set_ylabel("Temp (ºC)")

        self.ax2.legend(loc="upper left")
        self.ax2_temp.legend(loc="upper right")
        self.ax2.grid(True)

    def _update_graph(self, frame):
        """Atualiza as linhas do gráfico a cada frame da animação."""
        try:
            latest_data = self.lidar.get_read()
            if latest_data:
                dist, stren, temp = latest_data

                self.x_data.append(len(self.x_data))
                self.dist_data.append(dist)
                self.strength_data.append(stren)
                self.temp_data.append(temp)

                if len(self.x_data) > self.max_points:
                    self.x_data.pop(0)
                    self.dist_data.pop(0)
                    self.strength_data.pop(0)
                    self.temp_data.pop(0)
        except Exception as e:
            print(f"Erro de leitura: {e}")

        self.dist_line.set_data(range(len(self.dist_data)), self.dist_data)
        self.strengh_line.set_data(range(len(self.strength_data)), self.strength_data)
        self.temp_line.set_data(range(len(self.temp_data)), self.temp_data)

        self.ax1.set_xlim(0, self.max_points)
        self.ax2.set_xlim(0, self.max_points)

        return self.dist_line, self.strengh_line, self.temp_line

    def run(self):
        print("Iniciando monitoramento. Feche a janela do gráfico para encerrar.")
        self.ani = FuncAnimation(
            self.fig, 
            self._update_graph, 
            interval=self.interval_ms, 
            cache_frame_data=False
        )
        plt.show()

    def cleanup(self):
        print("\nDesligando o Lidar...")
        try:
            self.lidar.stop()
        except Exception as e:
            print(f"Erro ao desligar o Lidar: {e}")
