from .pcaServosInterface import PCAServosInterface
from .exceptions import BoardNotFoundModule, BusionNotFoundModule, PCA9685NotFoundModule
import time 

try:
    import board 
    aBoard = True
    
except:
    aBoard = False 

try: 
    import busio 
    aBusio = True
    
except:
    aBusio = False    

try: 
    from adafruit_pca9685 import PCA9685
    aPCA9685 = True
except:
    aPCA9685 = False

class PCAServos(PCAServosInterface):
    def __init__(self, frequency: int = 50):
        
        if not aBusio:
            raise BusionNotFoundModule("O módulo Busio não foi encontrado, verifique se você está no ambiente da Raspberry")
        
        if not aBoard:
            raise BoardNotFoundModule("O módulo Board não foi encontrado, verifique se você está no ambiente da Raspberry")
        
        if not aPCA9685:
            raise PCA9685NotFoundModule("O módulo PCA9685 não foi encontrado, verifique se você está no ambiente da Raspberry")
        
        i2c = busio.I2C(board.SCL, board.SDA) # Define canal de comunicação
        
        self.pca = PCA9685(i2c) # Instância objeto 
        self.pca.frequency = frequency # define frequência dos servos
        self._all_channels = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15) # todos os canais do PCA9685 

    def set_servo_speed(self, channels: tuple, speed: float):
        min_pulse = 2000 # pulso pwm mínimo 
        max_pulse = 8000 # pulso pwm máximo
        neutral = 5000 # pulso pwm neutro
        
        pulse = int(neutral + speed * (max_pulse - min_pulse) / 2) # formula para o pulso em função da velocidade
        
        pulse = max(min_pulse, min(max_pulse, pulse)) # define o pulso possivel
        
        for channel in channels: # velocidade para cada canal
            pca.channels[channel].duty_cycle = pulse # define a velocidade 
            
    
    def stop(self, channels):
        self.set_servo_speed(channels, 0) # define a velocidade como 0, parando os servos
    
    def forward(self, channels, speed):
        new_speed = abs(speed) # torna a velocidade >= 0
        self.set_servo_speed(channels, new_speed)
        
    def backward(self, channels, speed):
        new_speed = -(abs(speed)) # torna a velocidade <= 0
        self.set_servo_speed(channels, new_speed)
        
    def stop_all(self):
        self.stop(self._all_channels) # Para todos os servos
        
    def move_angle(self, channels, angle):
        pass
    
    def move_multiplo_angle(self, channels_angles):
        pass
    
    def cleaup(self):
        self.stop_all() # para todos os servos 
        self.pca.deinit() # libera os recursos do PCA9685