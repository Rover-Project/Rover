import pytest
import sys
from unittest.mock import MagicMock

# 1. Simulamos as bibliotecas de hardware para que o teste rode no Windows/PC comum
sys.modules['board'] = MagicMock()
sys.modules['busio'] = MagicMock()
sys.modules['adafruit_pca9685'] = MagicMock()
sys.modules['adafruit_motor'] = MagicMock()

# Agora podemos importar nossa biblioteca com segurança
from pca9685.servos import Servo

def test_servo_aceita_angulo_valido():
    # Cria um PCA falso (mock) e inicializa o servo
    pca_mock = MagicMock()
    meu_servo = Servo(pca=pca_mock, channel=0)
    
    # Atribui 90 graus (deve funcionar sem disparar erros)
    meu_servo.angle = 90.0
    
    # Verifica se a classe repassou o valor corretamente para o backend da Adafruit
    assert meu_servo._adafruit_servo.angle == 90.0

def test_servo_rejeita_angulo_negativo():
    pca_mock = MagicMock()
    meu_servo = Servo(pca=pca_mock, channel=1)
    
    # Verifica se ao mandar um ângulo negativo, a classe levanta a exceção ValueError
    with pytest.raises(ValueError, match="Ângulo inválido"):
        meu_servo.angle = -15.0

def test_servo_rejeita_angulo_acima_do_limite():
    pca_mock = MagicMock()
    meu_servo = Servo(pca=pca_mock, channel=2)
    
    # Verifica se ao mandar um ângulo > 180, a classe levanta a exceção
    with pytest.raises(ValueError, match="Ângulo inválido"):
        meu_servo.angle = 200.0
