"""
Módulo de controle avançado com compensação de motores e calibração.
Tenta ajustes pontuais para compensar diferenças entre motores.
"""
class Calibration:
    """
    Gerencia calibração de motores para compensar diferenças de comportamento.
    """
    
    def __init__(self, right:float, left:float):
        """
        Inicializa a classe de calibração
        Args:
            right (float): coeficiente de calibração para o motor direito.
            left (float): coeficiente de calibração para o motor esquerdo.
        """

        self.left = left 
        self.right = right
    
    def get_calibration(self, left_speed:float, right_speed:float) -> tuple[float, float]:
        """
        Aplica os coeficientes de calibração para a velocidade velocidades.
        
        Args:
            left_speed (float): Velocidade desejada motor esquerdo
            right_speed (float): Velocidade desejada motor direito
        
        Returns:
            tuple: (left_speed_calibrated, right_speed_calibrated)
        """
        left_calibrated = left_speed * self.left
        right_calibrated = right_speed * self.right
        
        return right_calibrated, left_calibrated
    
    def set_calibration(self, right: float, left: float):
        """
        Define novos coeficiente de calibracao de acordo com os valores passados como parametro
        Args:
            left (float): coeficiente para o motor direito
            right (float): coeficiente para o motor esquerdo
        """
        
        self.right = right
        self.left = left