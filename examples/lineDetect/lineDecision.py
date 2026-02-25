from roverlib.modules.movement.PID import PID # type: ignore
from roverlib.modules.movement.robot import Robot # type: ignore
from roverlib.modules.movement.motorCalibration import Calibration # type: ignore
from roverlib.utils.config_manager import Config # type: ignore
import time
from pathlib import Path

class decision:
    def __init__(self):
        config = Config(Path(__file__).parent / "config.yaml")
        self.search_speed = 70
        self.motor_config = config.get("gpio")["motor"]
        self.x_speed = 40
        self.height = 640
        self.width = 640
        self.history = []
        self.max_history = 30
        # Implementar algo que, caso o Rover estiver no centro da pista, acelere ele por completo
        x_center = 640 / 2
        self.right_s = self.x_speed
        self.left_s = self.x_speed

        self.robot = Robot(
            left=self.motor_config["left"], 
            right=self.motor_config["right"],
            calibration=Calibration(
                right=self.motor_config["calibration"]["right"],
                left=self.motor_config["calibration"]["left"]
            )
        )
        
        self.pid_x = PID(
            kp=(self.x_speed / x_center),
            ki=1,
            kd=1
        )

    def decide(self, frame, lr_lines: tuple, target_line, drive_mode: str):
        if not lr_lines:
            print("Não foi iniciado ou não está identifcando linhas")
            return "Perdido ou não inicado", 0

        left_line = lr_lines[0]
        right_line = lr_lines[1]

        # Não encontrou linha em nenhum dos lados
        if not drive_mode:
            return "Selecione um modo", 0

        else:
            if len(self.history) > self.max_history:
                self.history.pop(0)
                self.history.append((left_line, right_line))
                center_cam = frame.shape[1] / 2

        # Duas linhas paralelas (Estrada)
        if drive_mode == "road":

            if left_line is None and right_line is None:
                if not self.history:
                    self.robot.turn_right(self.search_speed)
                    return "perdido", 0

                else:
                    self.robot.backfowards(self.x_speed, 2)
                    return "Voltando", 0
                
            if left_line and right_line:
                center_road = (left_line[1][0] + right_line[1][0]) / 2
                
            elif left_line and not right_line:
                center_road = left_line[1][0] + 100

            else:
                center_road = right_line[1][0] - 100

            # calculo do erro
            erro = center_cam - center_road

            adjustment = self.pid_x.controller_P(erro)

            self.left_s = (self.x_speed + adjustment)
            self.right_s = (self.x_speed - adjustment)

        elif drive_mode == "line": 
            # passa a linha que ele considerar existente 
            # para não alterar a lógica de args

            if target_line:
                center_line = target_line[1][0]
                erro = center_cam - center_line

                adjustment = self.pid_x.controller_P(erro)

                self.left_s = (self.x_speed - adjustment)
                self.right_s = (self.x_speed + adjustment)

            else: 
                print("Não foi possível formar target_line")
                return "perdido", 0

        self.robot.move(speed_left=self.left_s, speed_right=self.right_s)
        direcao = "Frente" if erro < 10 and erro > -10 else ("Direita" if erro < 0 else "Esquerda")

        return direcao, erro