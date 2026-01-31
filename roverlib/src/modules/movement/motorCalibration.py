"""
Módulo de controle avançado com compensação de motores e calibração.
Tenta ajustes pontuais para compensar diferenças entre motores.
"""
from utils.config_manager import Config


class MotorCalibration:
    """
    Gerencia calibração de motores para compensar diferenças de comportamento.
    """
    
    def __init__(self):
        """
        Inicializa o sistema de calibração.
        """
        self.loadCalibration() # Carrega os coeficientes de calibracao do arquivo config.yaml
        
    def loadCalibration(self):
        corrections_motors = Config.get("motor_calibration")
        
        # coeficientes de correção para os dois motores
        self.left_speed_correction =  corrections_motors["limiar_motor_esquerdo"]
        self.right_speed_correction =  corrections_motors["limiar_motor_direito"]
    
    def getCalibration(self, left_speed, right_speed):
        """
        Aplica fatores de calibração às velocidades.
        
        Args:
            left_speed (float): Velocidade desejada motor esquerdo
            right_speed (float): Velocidade desejada motor direito
        
        Returns:
            tuple: (left_speed_calibrated, right_speed_calibrated)
        """
        left_calibrated = left_speed * self.left_speed_correction
        right_calibrated = right_speed * self.right_speed_correction
        
        return left_calibrated, right_calibrated
    
    def setCalibration(self, left_calibration, right_calibration):
        """
        Define novos coeficiente de calibracao de acordo com os valores passados como parametro
        Args:
            left_calibration (_type_): coeficiente para o motor direito
            right_calibration (_type_): coeficiente para o motor esquerdo
        """
        
        calibration = {
            "motor_calibration": {
                "limiar_motor_direito": right_calibration, 
                "limiar_motor_esquerdo": left_calibration
            }
        }
        
        Config.setConfig(calibration)
        
        self.loadCalibration()