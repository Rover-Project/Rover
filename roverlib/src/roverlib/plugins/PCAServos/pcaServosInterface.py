from abc import ABC

class PCAServosInterface(ABC):
    """
    Interface para a implementação de plugins para o módulo PCA de controle multiplos de servos 360°
    """
    
    def set_servo_speed(self, channels: tuple, speed: int):
        """
        Define uma velocidade para os servos.
        Args:
            channels (tuple): canais assionados para essa ação
            speed (int): velocidade de rotação dos canais
        """
        pass
    
    def move_angle(self, channels: tuple, angle: float):
        """
        Define um ângulo para os servos passados como parâmetro
        Args:
            channels (tuple): Servos impactados 
            angle (float): Ângulo para os servos
        """
        pass
    
    def move_multiplo_angle(self, channels_angles: tuple[tuple[int, float]]):
        """
        Define ângulos de rotação para cada servos 
        Args:
            channels_angles: Uma lista de tuplas para cada canal, sendo cada tupla um par ordenado no formato: (channel, angle)
        """
    
    def forward(self, channels: tuple, speed: float):
        """
        Move o servo para frente, ou seja, com velocidade positiva
        Args:
            channels (tuple): Cannais impactados
            speed (float): velocidade de rotação
        """
        pass
    
    def backward(self, channels: tuple, speed: float):
        """
        Move o servo para trás, ou seja, com velocidade negativa.

        Args:
            channels (tuple): Canais impactados 
            speed (float): Velocidade de rotação
        """
        pass
    
    def stop(self, channels: tuple):
        """
        Para os canais listados 
        Args:
            channels (tuple): Canais impactados
        """
        pass
    
    def stop_all(self):
        """
        Para todos os canais
        """
        pass
    
    def cleaup(self):
        """Libera os recursos de hardware"""
        pass