from roverlib.plugins.lidar.exceptions import LidarDoNotRespond #type: ignore
from roverlib.plugins.lidar.lidar import Lidar #type: ignore
import serial #type: ignore
import time 

def run_test():
    lidar = Lidar()
    try:
        lidar.start()
    except Exception as e:
        print(f"Falha ao iniciar: {e}")
        return
    
    print("Iniciando leituras... Pressione Ctrl+C para parar.")
    while True:
        try:
            dist, strenght, temp = lidar.get_read()

            # Verifica se a leitura falhou (assumindo que get_read retorna None em erro)
            if dist is None:
                print("Aguardando dados válidos...")
                time.sleep(0.1)
                print(f"{dist} - {temp} - {strenght}")
                continue
            
            print(f"Distancia (cm): {dist}, Força: {strenght}, Temperatura: {temp} ")
            time.sleep(0.01)

        except KeyboardInterrupt as e:
            if hasattr(lidar, 'stop'):
                lidar.stop()
                print('Não deu certo ou foi interrompido')
                break

if __name__ == "__main__":
    run_test()
    