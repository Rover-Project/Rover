"""
Testes do controlador PID (sem hardware).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/modules/movement/tests
"""
import pytest

from roverlib.modules.movement import PID as pid_module
from roverlib.modules.movement.PID import PID


@pytest.fixture
def relogio(monkeypatch):
    """Relógio controlado: avance com relogio.append(t)."""
    tempos = [100.0]
    monkeypatch.setattr(pid_module.time, "time", lambda: tempos[-1])
    return tempos


def test_p():
    assert PID(kp=2, ki=5, kd=5).controller_P(3) == 6


def test_pd_usa_a_derivada_e_nao_a_integral(relogio):
    pid = PID(kp=1, ki=100, kd=2)
    assert pid.controller_PD(1.0) == 1.0          # 1ª chamada: só o proporcional
    relogio.append(100.5)
    # derivada = (2 - 1) / 0.5 = 2 -> 1*2 + 2*2 = 6 (ki não entra no PD)
    assert pid.controller_PD(2.0) == pytest.approx(6.0)
    relogio.append(101.0)
    assert pid.controller_PD(2.0) == pytest.approx(2.0)   # erro constante: derivada 0


def test_pid_integral_aceita_erro_negativo(relogio):
    pid = PID(kp=0, ki=1, kd=0)
    pid.controller_PID(-1.0)
    for t in (101, 102, 103):
        relogio.append(t)
        u = pid.controller_PID(-1.0)
    assert u == pytest.approx(-3.0)               # integral de -1 por 3 s


def test_pid_anti_windup_simetrico():
    pid = PID(kp=0, ki=1, kd=0, max_I=5)
    for _ in range(20):
        u = pid.controller_PID(10.0, dt=1)
    assert u == pytest.approx(5.0)
    for _ in range(40):
        u = pid.controller_PID(-10.0, dt=1)
    assert u == pytest.approx(-5.0)


def test_pid_com_dt_informado():
    pid = PID(kp=2, ki=1, kd=0.5)
    assert pid.controller_PID(1.0, dt=0.1) == pytest.approx(2 + 0.1)        # P + I (sem derivada na 1ª)
    # 2ª: P=4, I=(0.1 + 0.2)=0.3, D=0.5*(2-1)/0.1=5
    assert pid.controller_PID(2.0, dt=0.1) == pytest.approx(4 + 0.3 + 5)


def test_reset_recomeca(relogio):
    pid = PID(kp=1, ki=1, kd=1)
    pid.controller_PID(5.0, dt=1)
    pid.reset()
    assert pid.controller_PID(1.0) == 1.0          # sem integral nem derivada anteriores


def test_dt_invalido_nao_quebra():
    pid = PID(kp=1, ki=1, kd=1)
    assert pid.controller_PID(2.0, dt=0) == 2.0     # dt <= 0: só o proporcional
