from Robot import Robot
import time

robot = Robot(
    left=(17, 27),   # IN1, IN2 motor esquerdo
    right=(22, 23)   # IN3, IN4 motor direito
)

robot.forward(0.6)   # anda para frente com 60% da velocidade
time.sleep(2)

robot.left(0.5)      # vira para a esquerda
time.sleep(1)

robot.backward(1.0)  # volta com velocidade máxima
time.sleep(2)

robot.stop()

robot.clear()