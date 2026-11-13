"""
Testes do PanTilt em modo simulação (não precisa da Raspberry Pi).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/modules/pan_tilt/tests
"""
from unittest.mock import MagicMock

import pytest

from roverlib.modules.pan_tilt import pan_tilt as pt_module
from roverlib.modules.pan_tilt.pan_tilt import PanTilt
from roverlib.plugins.PCAServos.pca9685 import servos as pca_module
from roverlib.utils.simulation import SIMULATE_ENV


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    sleeps = []
    monkeypatch.setattr(pt_module.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.delenv(SIMULATE_ENV, raising=False)
    return sleeps


def criar(**kwargs):
    p = PanTilt(simulate=True, **kwargs)
    p._pan.verbose = p._tilt.verbose = False
    return p


# ---------- escolha do driver ----------

def test_sem_pca_cai_na_simulacao(monkeypatch, capsys):
    monkeypatch.setattr(pca_module, "PCA_AVAILABLE", False)
    p = PanTilt()
    assert p.simulated
    assert "servos simulados" in capsys.readouterr().out


def test_simulate_false_sem_pca_da_erro(monkeypatch):
    monkeypatch.setattr(pca_module, "PCA_AVAILABLE", False)
    with pytest.raises(RuntimeError, match="PCA9685 indisponível"):
        PanTilt(simulate=False)


def test_hardware_real_usa_canais_e_pulsos(monkeypatch):
    monkeypatch.setattr(pca_module, "PCA_AVAILABLE", True)
    pca = MagicMock()
    monkeypatch.setattr(pca_module, "PCAServos", MagicMock(return_value=pca))
    cont = MagicMock()
    pos = MagicMock()
    monkeypatch.setattr(pca_module, "ContinuousServo", cont)
    monkeypatch.setattr(pca_module, "Servo", pos)

    p = PanTilt(pan_channel=2, tilt_channel=3, address=0x41, tilt_pulse=(600, 2400))
    assert not p.simulated
    pca_module.PCAServos.assert_called_once_with(address=0x41)
    cont.assert_called_once_with(pca, 2, 500, 2500)
    pos.assert_called_once_with(pca, 3, 600, 2400)
    p.cleanup()
    pca.close.assert_called_once_with(keep_channels=(3,))   # TILT segura a câmera
    pos.return_value.detach.assert_not_called()
    cont.return_value.detach.assert_called_once()


def test_cleanup_sem_hold_desliga_o_tilt(monkeypatch):
    monkeypatch.setattr(pca_module, "PCA_AVAILABLE", True)
    pca = MagicMock()
    monkeypatch.setattr(pca_module, "PCAServos", MagicMock(return_value=pca))
    monkeypatch.setattr(pca_module, "ContinuousServo", MagicMock())
    pos = MagicMock()
    monkeypatch.setattr(pca_module, "Servo", pos)
    p = PanTilt(hold_tilt=False)
    p.cleanup()
    pca.close.assert_called_once_with(keep_channels=())
    pos.return_value.detach.assert_called_once()


def test_angulos_do_tilt_invalidos():
    with pytest.raises(ValueError):
        PanTilt(simulate=True, tilt_min=100, tilt_center=90)


# ---------- PAN (360°) ----------

def test_pan_velocidade_e_sentido():
    p = criar()
    p.pan_right(40)
    assert p._pan.throttle == pytest.approx(0.4)
    assert p.pan_speed == 40
    p.pan_left(25)
    assert p._pan.throttle == pytest.approx(-0.25)
    p.stop_pan()
    assert p._pan.throttle == 0
    assert p.pan_speed == 0


def test_pan_limita_velocidade():
    p = criar()
    p.pan(250)
    assert p._pan.throttle == 1.0
    assert p.pan_speed == 100


def test_pan_trim_e_invert():
    p = criar(pan_trim=0.05, pan_invert=True)
    assert p._pan.throttle == pytest.approx(0.05)   # parado = trim
    p.pan_right(50)
    assert p._pan.throttle == pytest.approx(-0.45)  # invertido, somado ao trim
    p.stop_pan()
    assert p._pan.throttle == pytest.approx(0.05)


def test_pan_com_duracao_para_ao_final(sem_espera):
    p = criar(pan_max=None)                # sem limite: espera a duração inteira
    p.pan_right(30, duration=0.5)
    assert sem_espera == [0.5]
    assert p._pan.throttle == 0


@pytest.mark.parametrize("graus, velocidade, duracao, sentido", [
    (25, 20, 0.2, 1),      # 125°/s a 20 -> 25° = 0,2 s
    (-40, 40, 0.2, -1),    # esquerda: 100°/s a 20 -> 200°/s a 40 -> 40° = 0,2 s
])
def test_pan_degrees_usa_a_velocidade_de_cada_sentido(sem_espera, graus, velocidade, duracao, sentido):
    p = criar(pan_degrees_per_second=(125, 100), pan_calibration_speed=20)
    assert p.pan_degrees(graus, speed=velocidade) == graus
    assert sem_espera == [pytest.approx(duracao)]
    assert p.pan_position == graus
    assert p._pan.throttle == 0


def test_pan_degrees_zero_nao_gira(sem_espera):
    p = criar()
    p.pan_degrees(0)
    assert sem_espera == []


def test_pan_to_respeita_os_limites(sem_espera):
    p = criar(pan_min=-50, pan_max=50, pan_degrees_per_second=100, pan_calibration_speed=20)
    assert p.pan_to(80) == 50              # limitado
    assert sem_espera == [pytest.approx(0.5)]
    assert p.pan_position == 50
    p.pan_right(30, duration=1)            # já no limite: não gira
    assert sem_espera == [pytest.approx(0.5)]
    p.center()
    assert p.pan_position == 0


def test_pan_com_duracao_para_no_limite(sem_espera):
    p = criar(pan_max=10, pan_degrees_per_second=100, pan_calibration_speed=20)
    p.pan_right(20, duration=5)            # 10° a 100°/s -> para em 0,1 s
    assert sem_espera == [pytest.approx(0.1)]


def test_posicao_estimada_pelo_tempo(monkeypatch):
    agora = [100.0]
    monkeypatch.setattr(pt_module.time, "monotonic", lambda: agora[0])
    p = criar(pan_degrees_per_second=(125, 100), pan_calibration_speed=20)
    p.pan_right(20)                        # sem duração: segue girando
    agora[0] += 0.2
    assert p.pan_position == pytest.approx(25)
    p.pan_left(40)
    agora[0] += 0.1
    p.stop_pan()
    assert p.pan_position == pytest.approx(5)
    agora[0] += 5                          # parado: não muda
    assert p.pan_position == pytest.approx(5)
    p.reset_pan_position()
    assert p.pan_position == 0


def test_giro_continuo_para_sozinho_no_limite():
    p = criar(pan_max=1, pan_degrees_per_second=100, pan_calibration_speed=100)
    p.pan_right(100)                       # 1° a 100°/s -> para em ~10 ms
    p._limit_timer.join(1)
    assert p.pan_speed == 0
    assert p.pan_position == pytest.approx(1)


def test_limites_invalidos():
    with pytest.raises(ValueError):
        PanTilt(simulate=True, pan_min=10)
    with pytest.raises(ValueError):
        PanTilt(simulate=True, pan_degrees_per_second=0)


# ---------- TILT (180°) ----------

def test_tilt_limites():
    p = criar(tilt_min=45, tilt_max=135)
    assert p.tilt_to(10) == 45
    assert p.tilt_to(170) == 135
    assert p._tilt.angle == 135


def test_tilt_up_down_a_partir_do_centro():
    p = criar(tilt_center=80)
    assert p.tilt_angle == 80          # antes de mover, vale o centro
    p.tilt_up(15)
    assert p.tilt_angle == 95
    p.tilt_down(30)
    assert p.tilt_angle == 65


def test_tilt_invert():
    p = criar(tilt_invert=True)
    p.tilt_to(60)
    assert p.tilt_angle == 60
    assert p._tilt.angle == 120        # ângulo físico espelhado


def test_tilt_suave_passo_a_passo(sem_espera):
    p = criar()
    p.tilt_to(90)
    angulos = []
    original = p._apply_tilt
    p._apply_tilt = lambda a: (angulos.append(a), original(a))
    p.tilt_to(100, smooth=True, step=3, delay=0.01)
    assert angulos == [93, 96, 99, 100]
    assert sem_espera == [0.01, 0.01, 0.01]


def test_center_e_cleanup(sem_espera):
    p = criar()
    p.pan_degrees(-30)
    p.tilt_to(30)
    p.center()
    assert p._pan.throttle == 0
    assert p.pan_position == 0
    assert p.tilt_angle == 90
    p.pan_degrees(20)
    p.tilt_to(40)
    p.cleanup()                            # volta a câmera para a frente
    assert (p.pan_position, p.tilt_angle) == (0, 90)
    p.cleanup()


def test_context_manager():
    with PanTilt(simulate=True) as p:
        p.tilt_to(45)
    assert p._pan.throttle == 0
