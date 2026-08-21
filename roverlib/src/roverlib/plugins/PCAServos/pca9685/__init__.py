"""
Rover PCA9685 Plugin
====================
Biblioteca própria para controle do módulo PCA9685 via I2C na Raspberry Pi.
Desenvolvida como parte de Iniciação Científica para controle de servomotores
embarcados em robô móvel (rover).

Módulos disponíveis:
    - PCA9685Driver  : comunicação I2C de baixo nível com o chip
    - PCAServos      : interface de alto nível para controle de servos
    - Servo          : abstração para servo convencional (0°–180°)
    - ContinuousServo: abstração para servo de rotação contínua (360°)
"""

from .driver import PCA9685Driver
from .servos import PCAServos, Servo, ContinuousServo

__all__ = ["PCA9685Driver", "PCAServos", "Servo", "ContinuousServo"]
__version__ = "1.0.0"
__author__  = "Rover IC Project"
