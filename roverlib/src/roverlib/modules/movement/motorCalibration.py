"""
Módulo de controle avançado com compensação de motores e calibração.
Tenta ajustes pontuais para compensar diferenças entre motores.
"""
class Calibration:
    """
    Compensa diferenças de velocidade entre os dois motores.

    Dois motores iguais raramente giram exatamente na mesma velocidade, e o Rover puxa
    para um lado em `forward()`. Cada lado recebe um coeficiente que multiplica a velocidade
    pedida: com `Calibration(right=0.95, left=1)`, o motor direito gira a 95% do pedido.
    """
    
    def __init__(self, right:float, left:float):
        """
        Args:
            right (float): coeficiente do motor direito (1 = sem correção).
            left (float): coeficiente do motor esquerdo (1 = sem correção).
        """

        self.left = left 
        self.right = right
    
    def get_calibration(self, left_speed:float, right_speed:float) -> tuple[float, float]:
        """
        Aplica os coeficientes às velocidades pedidas.

        Args:
            left_speed (float): velocidade pedida para o motor esquerdo.
            right_speed (float): velocidade pedida para o motor direito.

        Returns:
            tuple: `(direita_calibrada, esquerda_calibrada)`. Atenção: a ordem é **direita, esquerda**,
                a inversa dos argumentos.
        """
        left_calibrated = left_speed * self.left
        right_calibrated = right_speed * self.right
        
        return right_calibrated, left_calibrated
    
    def set_calibration(self, right: float, left: float):
        """
        Troca os coeficientes de calibração.

        Args:
            right (float): novo coeficiente do motor direito.
            left (float): novo coeficiente do motor esquerdo.
        """
        
        self.right = right
        self.left = left