from roverlib.modules.movement.PID import PID # type: ignore
from roverlib.modules.movement.robot import Robot # type: ignore
from roverlib.modules.movement.motorCalibration import Calibration # type: ignore
from roverlib.utils.config_manager import Config # type: ignore
import time
from pathlib import Path

class decision:
    def __init__(self):
        config = Config(Path(__file__).parent / "config.yaml")
        self.search_speed = 60 # Velocidade padrao de busca
        self.motor_config = config.get("gpio")["motor"] # Arquivo de configuracao dos motores
        self.line_speed = 40 # Velocidade utilizada para seguir a linha
        self.height = 640 
        self.width = 640
        self.history = [] # memoria para corrigir um desvio de percurso
        self.max_history = 30 # Limite de deteccoes na memoria
        self.x_center = self.width / 2 # Centro da cam
        self.right_s = self.x_speed # Velocidade padrao para motor direito
        self.left_s = self.x_speed # Velocidade padrao para motor esquerdo

        self.robot = Robot(
            left=self.motor_config["left"], 
            right=self.motor_config["right"],
            calibration=Calibration(
                right=self.motor_config["calibration"]["right"],
                left=self.motor_config["calibration"]["left"]
            )
        )
        
        self.pid_x = PID(
            kp=(self.x_speed / self.x_center),
            ki=1,
            kd=1
        )

    def decide(self, frame, lr_lines: tuple, target_line, drive_mode: str):
        # Se nao houver um modo selecionado
        if not drive_mode:
            return "Selecione um modo", 0
        
        # Define o centro da camera para o calculo do erro
        center_cam = frame.shape[1] / 2

        # Duas linhas paralelas (Estrada)
        if drive_mode == "road":
            # Se a tupla de linhas left e right nao for none:
            if lr_lines:
                left_line = lr_lines[0]
                right_line = lr_lines[1]

                if len(self.history) > self.max_history:
                    self.history.pop(0)

                self.history.append((left_line, right_line))
            
            # Se for none, define left e right como none
            else: 
                left_line = None
                right_line = None

                if not self.history:
                    self.robot.turn_right(self.search_speed)
                    return "perdido", 0

                else:
                    self.robot.backfowards(self.x_speed, 2)
                    return "voltando", 0
            
            # Se tem as duas linhas, centro da pista = (x1 + x2) / 2
            if left_line and right_line:
                center_road = (left_line[1][0] + right_line[1][0]) / 2
                
            elif left_line and not right_line:
                center_road = left_line[1][0] + 100

            else:
                center_road = right_line[1][0] - 100

            # calculo do erro
            erro = center_cam - center_road
            # Ajuste de velocidad
            adjustment = self.pid_x.controller_P(erro)
            # Atribuicao dos Velocidade dos motores esquerdo e direito 
            self.left_s = (self.x_speed + adjustment)
            self.right_s = (self.x_speed - adjustment)

        # Linha unica (Competicao)
        elif drive_mode == "line": 
            # Se a linha alvo for detectada
            if target_line:

                if len(self.history) > self.max_history:
                    self.history.pop(0)

                self.history.append(target_line)

                # center_line = posicao x da linha
                center_line = target_line[1][0]
                erro = center_cam - center_line

                adjustment = self.pid_x.controller_P(erro)

                self.left_s = (self.x_speed - adjustment)
                self.right_s = (self.x_speed + adjustment)

            else: 
                if not self.history:
                    self.robot.turn_right(self.search_speed)
                    return "perdido", 0

                else:
                    self.robot.backfowards(self.x_speed, 2)
                    return "Voltando", 0

        self.robot.move(speed_left=self.left_s, speed_right=self.right_s)
        direcao = "Frente" if erro < 10 and erro > -10 else ("Direita" if erro < 0 else "Esquerda")

        return direcao, erro