# Definições de constantes para o projeto Rover

# Mapeamento de pinos GPIO (usando a numeração BCM) para a Ponte-H L298N
# Estes são valores de exemplo. O usuário deve ajustá-los de acordo com a fiação real.

# Motor Esquerdo
MOTOR_ESQUERDO_IN1 = 17  # Pino de direção 1
MOTOR_ESQUERDO_IN2 = 27  # Pino de direção 2
MOTOR_ESQUERDO_ENA = 22  # Pino PWM para controle de velocidade

# Motor Direito
MOTOR_DIREITO_IN3 = 23  # Pino de direção 3
MOTOR_DIREITO_IN4 = 24  # Pino de direção 4
MOTOR_DIREITO_ENB = 25  # Pino PWM para controle de velocidade

# Configurações da Câmera
CAMERA_RESOLUTION = (3280, 2464) # Resolução máxima do sensor IMX219
CAMERA_FPS = 30 # Taxa de quadros (Frames per Second)
CAMERA_PREVIEW_RESOLUTION = (640, 480) # Resolução para processamento de visão em tempo real
