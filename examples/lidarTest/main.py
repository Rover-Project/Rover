from roverlib.plugins.lidar.lidar import Lidar
import serial
import time 

def run_test():
    lidar = Lidar()
    lidar.start()
    while True:
        try:
            dist, strenght, temp = lidar.get_read()
            print(f"Distancia (cm): {dist}, Força: {strenght}, Temperatura: {temp} ")
            time.sleep(0.01)
        except KeyboardInterrupt as e:
            lidar.kill()
            print('Não deu certo ou foi interrompido')
            break

if __name__ == "__main__":
    run_test()
    