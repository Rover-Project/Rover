from roverlib.plugins.lidar.exceptions import LidarDoNotRespond
from roverlib.plugins.lidar.lidar import Lidar
import serial
import time 

def run_test():
    lidar = Lidar()
    lidar.start()
    while True:
        try:
            dist, strenght, temp = lidar.get_read()

            if not dist or not strenght or not temp:
                print("Alguns dos valores deu None")
                print(f"{dist} - {temp} - {strenght}")
                raise LidarDoNotRespond("Não foi possível realizar uma leitura satisfatoria")
            
            print(f"Distancia (cm): {dist}, Força: {strenght}, Temperatura: {temp} ")
            time.sleep(0.01)
        except KeyboardInterrupt as e:
            lidar.stop()
            print('Não deu certo ou foi interrompido')
            break

if __name__ == "__main__":
    run_test()
    