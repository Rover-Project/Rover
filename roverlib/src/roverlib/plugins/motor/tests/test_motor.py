"""
Testes do plugin motor (rodam no PC: o plugin pin é substituído por um falso).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/motor
"""
from unittest.mock import MagicMock

import pytest

from roverlib.exceptions import RoverLibError
from roverlib.plugins import motor as motor_package
from roverlib.plugins.motor import motorDriver
from roverlib.plugins.motor import (
    MotorDriver, VirtualMotor, MotorInterface,
    DirectionInvalidMotorError, UninitializedMotorError, MotorCreationError,
)
from roverlib.plugins.pin import PinMode


@pytest.fixture
def pinos(monkeypatch):
    """Pin falso: guarda os pinos criados para inspeção."""
    criados = {}

    def fabrica(numero, modo):
        pino = MagicMock(name=f"Pin({numero})")
        pino.modo = modo
        criados[numero] = pino
        return pino

    monkeypatch.setattr(motorDriver, "PIN_AVAILABLE", True)
    monkeypatch.setattr(motorDriver, "Pin", fabrica)
    return criados


def ultimo_pwm(pino):
    return pino.pwm.call_args.args


# ---------- API e exceções ----------

def test_api_publica_do_pacote():
    assert {"MotorDriver", "VirtualMotor", "MotorInterface", "HARDWARE_AVAILABLE"} <= set(motor_package.__all__)
    assert issubclass(MotorDriver, MotorInterface) and issubclass(VirtualMotor, MotorInterface)


def test_caminho_antigo_continua_funcionando():
    from roverlib.plugins.motor.vitualMotor import VirtualMotor as Antigo
    assert Antigo is VirtualMotor


def test_excecoes_compativeis():
    assert issubclass(MotorCreationError, ImportError)          # antes era ImportError
    assert issubclass(DirectionInvalidMotorError, RoverLibError)
    assert issubclass(UninitializedMotorError, RoverLibError)


# ---------- MotorDriver ----------

def test_sem_gpio_gera_motor_creation_error(monkeypatch):
    monkeypatch.setattr(motorDriver, "PIN_AVAILABLE", False)
    with pytest.raises(MotorCreationError):
        MotorDriver((17, 27))


def test_initialize_configura_os_dois_pinos(pinos):
    m = MotorDriver((17, 27), pwm_frequency=500)
    m.initialize()
    assert set(pinos) == {17, 27}
    assert all(p.modo == PinMode.DIGITAL_OUT for p in pinos.values())
    assert ultimo_pwm(pinos[17]) == (0.0, 500) and ultimo_pwm(pinos[27]) == (0.0, 500)
    m.initialize()  # segunda chamada não recria os pinos
    assert len(pinos) == 2


@pytest.mark.parametrize("direcao, esperado_in1, esperado_in2", [
    ("forward", 0.6, 0.0),
    ("BACKWARD", 0.0, 0.6),
    ("stop", 0.0, 0.0),
])
def test_set_movement(pinos, direcao, esperado_in1, esperado_in2):
    m = MotorDriver((17, 27))
    m.initialize()
    m.set_movement(60, direcao)
    assert ultimo_pwm(pinos[17])[0] == pytest.approx(esperado_in1)
    assert ultimo_pwm(pinos[27])[0] == pytest.approx(esperado_in2)


def test_velocidade_limitada_a_100(pinos):
    m = MotorDriver((17, 27))
    m.initialize()
    m.set_movement(250)
    assert ultimo_pwm(pinos[17])[0] == 1.0


def test_erros_de_uso(pinos):
    m = MotorDriver((17, 27))
    with pytest.raises(UninitializedMotorError):
        m.set_movement(50)
    m.initialize()
    with pytest.raises(DirectionInvalidMotorError):
        m.set_movement(50, "lado")


def test_cleanup_para_e_libera(pinos):
    m = MotorDriver((17, 27))
    m.initialize()
    m.set_movement(80)
    m.cleanup()
    for p in pinos.values():
        assert ultimo_pwm(p)[0] == 0.0
        p.release.assert_called_once()
    m.cleanup()  # chamar de novo não deve dar erro


# ---------- VirtualMotor ----------

def test_virtual_guarda_estado():
    m = VirtualMotor((1, 2), "teste", verbose=False)
    m.initialize()
    m.set_movement(40, "backward")
    assert (m.direction, m.speed) == ("BACKWARD", 40)
    m.stop()
    assert (m.direction, m.speed) == ("STOP", 0)


def test_virtual_erros_de_uso():
    m = VirtualMotor((1, 2), verbose=False)
    with pytest.raises(UninitializedMotorError):
        m.set_movement(50)
    m.initialize()
    with pytest.raises(DirectionInvalidMotorError):
        m.set_movement(50, "lado")
