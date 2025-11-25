"""
Módulo de controle avançado com compensação de motores e calibração.
Tenta ajustes pontuais para compensar diferenças entre motores.
"""
import json
import os
from robot import Robot


class MotorCalibration:
    """
    Gerencia calibração de motores para compensar diferenças de comportamento.
    """
    
    def __init__(self, calibration_file="motor_calibration.json"):
        """
        Inicializa o sistema de calibração.
        
        Args:
            calibration_file (str): Caminho para arquivo de calibração
        """
        self.calibration_file = calibration_file
        self.calibration = {
            'left_motor_bias': 1.0,   # Fator de correção para motor esquerdo
            'right_motor_bias': 1.0,  # Fator de correção para motor direito
            'min_speed_threshold': 5.0  # Velocidade mínima efetiva
        }
        self.load_calibration()
    
    def load_calibration(self):
        """Carrega calibração do arquivo, se existir."""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    self.calibration.update(json.load(f))
                print(f"Calibração carregada de {self.calibration_file}")
            except Exception as e:
                print(f"Erro ao carregar calibração: {e}. Usando valores padrão.")
        else:
            print("Arquivo de calibração não encontrado. Usando valores padrão.")
    
    def save_calibration(self):
        """Salva calibração atual no arquivo."""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration, f, indent=2)
            print(f"Calibração salva em {self.calibration_file}")
        except Exception as e:
            print(f"Erro ao salvar calibração: {e}")
    
    def set_motor_bias(self, left_bias=1.0, right_bias=1.0):
        """
        Define fatores de correção para os motores.
        
        Args:
            left_bias (float): Fator de correção motor esquerdo (ex: 1.1 = 10% mais rápido)
            right_bias (float): Fator de correção motor direito
        """
        self.calibration['left_motor_bias'] = left_bias
        self.calibration['right_motor_bias'] = right_bias
        self.save_calibration()
    
    def apply_calibration(self, left_speed, right_speed):
        """
        Aplica fatores de calibração às velocidades.
        
        Args:
            left_speed (float): Velocidade desejada motor esquerdo
            right_speed (float): Velocidade desejada motor direito
        
        Returns:
            tuple: (left_speed_calibrated, right_speed_calibrated)
        """
        left_calibrated = left_speed * self.calibration['left_motor_bias']
        right_calibrated = right_speed * self.calibration['right_motor_bias']
        
        # Aplica threshold mínimo
        min_threshold = self.calibration['min_speed_threshold']
        if abs(left_calibrated) < min_threshold and left_calibrated != 0:
            left_calibrated = min_threshold if left_calibrated > 0 else -min_threshold
        if abs(right_calibrated) < min_threshold and right_calibrated != 0:
            right_calibrated = min_threshold if right_calibrated > 0 else -min_threshold
        
        return left_calibrated, right_calibrated


class MovementControl(Robot):
    """
    Controle avançado de movimento com compensação e calibração.
    """
    
    def __init__(self, driver=None, pwm_frequency=100, calibration_file="motor_calibration.json"):
        """
        Inicializa o controle avançado de movimento.
        
        Args:
            driver: Driver de motores (opcional)
            pwm_frequency (int): Frequência PWM
            calibration_file (str): Arquivo de calibração
        """
        super().__init__(driver, pwm_frequency)
        self.calibration = MotorCalibration(calibration_file)
    
    def forward(self, speed=50, duration=None, use_calibration=True):
        """
        Move para frente com calibração opcional.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos
            use_calibration (bool): Se True, aplica calibração de motores
        """
        if use_calibration:
            left_speed, right_speed = self.calibration.apply_calibration(speed, speed)
        else:
            left_speed, right_speed = speed, speed
        
        self.move(left_speed, right_speed)
        
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
    
    def backward(self, speed=50, duration=None, use_calibration=True):
        """
        Move para trás com calibração opcional.
        
        Args:
            speed (float): Velocidade de 0 a 100
            duration (float, optional): Duração em segundos
            use_calibration (bool): Se True, aplica calibração de motores
        """
        if use_calibration:
            left_speed, right_speed = self.calibration.apply_calibration(-speed, -speed)
        else:
            left_speed, right_speed = -speed, -speed
        
        self.move(left_speed, right_speed)
        
        if duration is not None:
            import time
            time.sleep(duration)
            self.stop()
    
    def move(self, speed_left, speed_right, use_calibration=True):
        """
        Controla motores com calibração opcional.
        
        Args:
            speed_left (float): Velocidade motor esquerdo (-100 a 100)
            speed_right (float): Velocidade motor direito (-100 a 100)
            use_calibration (bool): Se True, aplica calibração
        """
        if use_calibration:
            speed_left, speed_right = self.calibration.apply_calibration(speed_left, speed_right)
        
        super().move(speed_left, speed_right)
    
    def calibrate_motors(self, left_bias=1.0, right_bias=1.0):
        """
        Define fatores de calibração dos motores.
        
        Args:
            left_bias (float): Fator motor esquerdo (1.0 = sem correção, 1.1 = 10% mais rápido)
            right_bias (float): Fator motor direito
        """
        self.calibration.set_motor_bias(left_bias, right_bias)
        print(f"Calibração atualizada: Esquerdo={left_bias:.2f}, Direito={right_bias:.2f}")

