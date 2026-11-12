"""
Testes do plugin PCAServos sem hardware (as classes da Adafruit são substituídas por mocks).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/PCAServos/tests
"""
from unittest.mock import MagicMock

import pytest

from roverlib.plugins.PCAServos.pca9685 import servos as servos_mod
from roverlib.plugins.PCAServos.pca9685 import VirtualServo, VirtualContinuousServo


@pytest.fixture
def servo_adafruit_falso(monkeypatch):
    """Substitui o módulo adafruit_motor.servo (ausente no PC) por um mock."""
    monkeypatch.setattr(servos_mod, "servo", MagicMock(), raising=False)


def criar_servo(channel):
    pca_mock = MagicMock()
    return servos_mod.Servo(pca=pca_mock, channel=channel)


def test_servo_aceita_angulo_valido(servo_adafruit_falso):
    meu_servo = criar_servo(0)
    meu_servo.angle = 90.0
    assert meu_servo._adafruit_servo.angle == 90.0


def test_servo_rejeita_angulo_negativo(servo_adafruit_falso):
    meu_servo = criar_servo(1)
    with pytest.raises(ValueError, match="Ângulo inválido"):
        meu_servo.angle = -15.0


def test_servo_rejeita_angulo_acima_do_limite(servo_adafruit_falso):
    meu_servo = criar_servo(2)
    with pytest.raises(ValueError, match="Ângulo inválido"):
        meu_servo.angle = 200.0


def test_pcaservos_sem_i2c_explica_o_erro(monkeypatch):
    monkeypatch.setattr(servos_mod, "PCA_AVAILABLE", False)
    with pytest.raises(RuntimeError, match="PCA9685 indisponível"):
        servos_mod.PCAServos()


# ---------- servos simulados ----------

def test_virtual_servo():
    s = VirtualServo(channel=1, verbose=False)
    assert s.angle is None
    s.angle = 45
    assert s.angle == 45
    s.center()
    assert s.angle == 90
    with pytest.raises(ValueError):
        s.angle = 181


def test_virtual_continuous_servo_limita_velocidade():
    s = VirtualContinuousServo(channel=0, verbose=False)
    s.throttle = 2
    assert s.throttle == 1.0
    s.throttle = -0.5
    assert s.throttle == -0.5
    s.stop()
    assert s.throttle == 0.0
