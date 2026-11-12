"""
Testes do Robot em modo simulação (não precisa da Raspberry Pi).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/modules/movement/tests
"""
import pytest

from roverlib.modules.movement import robot as robot_module
from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.motorCalibration import Calibration
from roverlib.plugins.motor import motorDriver
from roverlib.plugins.motor.virtual import VirtualMotor


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    """Evita que os testes esperem de verdade pelo `duration`."""
    sleeps = []
    monkeypatch.setattr(robot_module.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.delenv(robot_module.SIMULATE_ENV, raising=False)
    return sleeps


@pytest.fixture
def robo():
    r = Robot(right=(17, 27), left=(22, 23), simulate=True)
    r.left_motor.verbose = r.right_motor.verbose = False
    yield r
    r.cleanup()


def estado(r):
    return (r.left_motor.direction, r.left_motor.speed), (r.right_motor.direction, r.right_motor.speed)


# ---------- escolha do driver ----------

def test_simulate_true_usa_motor_virtual(robo):
    assert robo.simulated is True
    assert isinstance(robo.left_motor, VirtualMotor)
    assert isinstance(robo.right_motor, VirtualMotor)
    assert (robo.left_motor.in1, robo.left_motor.in2) == (22, 23)
    assert (robo.right_motor.in1, robo.right_motor.in2) == (17, 27)


def test_sem_gpio_cai_na_simulacao(monkeypatch, capsys):
    monkeypatch.setattr(motorDriver, "PIN_AVAILABLE", False)
    r = Robot(right=(17, 27), left=(22, 23))
    assert r.simulated is True
    assert "simulados" in capsys.readouterr().out


def test_variavel_de_ambiente_forca_simulacao(monkeypatch):
    monkeypatch.setattr(motorDriver, "PIN_AVAILABLE", True)
    monkeypatch.setenv(robot_module.SIMULATE_ENV, "1")
    r = Robot(right=(17, 27), left=(22, 23))
    assert r.simulated is True


def test_simulate_false_sem_gpio_da_erro(monkeypatch):
    monkeypatch.setattr(motorDriver, "PIN_AVAILABLE", False)
    with pytest.raises(ImportError):
        Robot(right=(17, 27), left=(22, 23), simulate=False)


def test_calibracao_nao_e_compartilhada():
    a = Robot(right=(1, 2), left=(3, 4), simulate=True)
    b = Robot(right=(1, 2), left=(3, 4), simulate=True)
    a.calibration.set_calibration(right=0.5, left=0.5)
    assert (b.calibration.right, b.calibration.left) == (1, 1)


# ---------- movimentos ----------

def test_forward_e_backward(robo):
    robo.forward(60)
    assert estado(robo) == (("FORWARD", 60), ("FORWARD", 60))
    robo.backward(40)
    assert estado(robo) == (("BACKWARD", 40), ("BACKWARD", 40))


def test_forward_aplica_calibracao():
    r = Robot(right=(1, 2), left=(3, 4), calibration=Calibration(right=0.5, left=1), simulate=True)
    r.forward(80)
    assert estado(r) == (("FORWARD", 80), ("FORWARD", 40))


def test_giros_no_proprio_eixo(robo):
    robo.turn_left(50)
    assert estado(robo) == (("BACKWARD", 50), ("FORWARD", 50))
    robo.turn_right(50)
    assert estado(robo) == (("FORWARD", 50), ("BACKWARD", 50))


def test_duration_para_o_robo(robo, sem_espera):
    robo.forward(50, duration=2)
    assert sem_espera == [2]
    assert estado(robo) == (("STOP", 0), ("STOP", 0))


def test_velocidade_limitada_a_100(robo):
    robo.forward(150)
    assert robo.left_motor.speed == 100


def test_stop_e_cleanup(robo):
    robo.forward(50)
    robo.stop()
    assert estado(robo) == (("STOP", 0), ("STOP", 0))
    robo.cleanup()
    assert robo.left_motor._initialized is False


def test_context_manager():
    with Robot(right=(1, 2), left=(3, 4), simulate=True) as r:
        r.forward(50)
    assert r.left_motor._initialized is False


def test_move_com_velocidades_iguais(robo):
    robo.move(speed_right=30, speed_left=-30)
    assert estado(robo) == (("BACKWARD", 30), ("FORWARD", 30))


def test_move_com_velocidades_diferentes(robo):
    robo.move(speed_right=80, speed_left=20)
    assert estado(robo) == (("FORWARD", 20), ("FORWARD", 80))


def test_move_sentidos_opostos_e_zero(robo):
    robo.move(speed_right=-70, speed_left=0)
    assert estado(robo) == (("STOP", 0), ("BACKWARD", 70))


def test_move_aplica_calibracao_no_lado_certo():
    r = Robot(right=(1, 2), left=(3, 4), calibration=Calibration(right=0.5, left=1), simulate=True)
    r.move(speed_right=80, speed_left=20)
    assert estado(r) == (("FORWARD", 20), ("FORWARD", 40))


@pytest.mark.parametrize("graus, metodo, duracao", [(90, "turn_right", 3.0), (-180, "turn_left", 6.0)])
def test_turn_degrees(robo, sem_espera, graus, metodo, duracao):
    robo.turn_degrees(graus, time_to_turn=12)
    assert sem_espera == [pytest.approx(duracao)]
    assert estado(robo) == (("STOP", 0), ("STOP", 0))


def test_turn_degrees_zero_nao_gira(robo, sem_espera):
    robo.turn_degrees(0)
    assert sem_espera == []
