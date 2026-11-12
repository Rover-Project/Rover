"""
Testes do plugin pin.

- Testes comuns: rodam no PC, com um módulo nativo falso.
- Testes de hardware (@pytest.mark.hardware): exigem a Raspberry Pi.

Executar (na pasta roverlib/):
    python -m pytest src/roverlib/plugins/pin                 # PC
    ROVER_TEST_PIN=21 python -m pytest -m hardware src/roverlib/plugins/pin   # Raspberry Pi
"""
import os
from unittest.mock import MagicMock

import pytest

from roverlib.exceptions import HardwareNotAvailable, RoverLibError
from roverlib.plugins import pin as pin_package
from roverlib.plugins.pin import pin as pin_module
from roverlib.plugins.pin import Pin, PinMode, PinNotAvailable


@pytest.fixture
def nativo_falso(monkeypatch):
    """Substitui o módulo nativo (_pin_native) por um mock."""
    native = MagicMock()
    monkeypatch.setattr(pin_module, "_native", native)
    monkeypatch.setattr(pin_module, "HARDWARE_AVAILABLE", True)
    return native


# ---------- sem hardware ----------

def test_api_publica_do_pacote():
    assert pin_package.Pin is pin_module.Pin
    assert {"Pin", "PinMode", "HARDWARE_AVAILABLE", "PinNotAvailable"} <= set(pin_package.__all__)
    assert {"DIGITAL_IN", "DIGITAL_OUT", "PWM"} <= {m.name for m in PinMode}


def test_sem_modulo_nativo_gera_erro_claro(monkeypatch):
    monkeypatch.setattr(pin_module, "HARDWARE_AVAILABLE", False)
    with pytest.raises(PinNotAvailable, match="Raspberry Pi"):
        Pin(17, PinMode.DIGITAL_OUT)


def test_excecao_herda_das_bases():
    # Compatível com quem já tratava RuntimeError, e capturável como erro da RoverLib
    assert issubclass(PinNotAvailable, RuntimeError)
    assert issubclass(PinNotAvailable, HardwareNotAvailable)
    assert issubclass(PinNotAvailable, RoverLibError)


# ---------- delegação ao módulo nativo ----------

def test_cria_pino_nativo(nativo_falso):
    Pin(17, PinMode.DIGITAL_OUT)
    nativo_falso.Pin.assert_called_once_with(17, PinMode.DIGITAL_OUT)


def test_digital(nativo_falso):
    pino = Pin(17, PinMode.DIGITAL_OUT)
    nativo = nativo_falso.Pin.return_value
    pino.on()
    pino.off()
    pino.write(1)
    assert [c.args for c in nativo.write.call_args_list] == [(1,), (0,), (1,)]
    nativo.read.return_value = 1
    assert pino.read() == 1


def test_pwm(nativo_falso):
    pino = Pin(18, PinMode.PWM)
    nativo = nativo_falso.Pin.return_value
    pino.pwm(0.075)
    nativo.pwmWrite.assert_called_with(0.075, 50.0)
    pino.pwm(0.5, 1000)
    nativo.pwmWrite.assert_called_with(0.5, 1000)
    pino.stop_pwm()
    nativo.pwmStop.assert_called_once()


def test_propriedades(nativo_falso):
    pino = Pin(18, PinMode.PWM)
    nativo = nativo_falso.Pin.return_value
    nativo.getDuty.return_value = 0.25
    nativo.getFrequency.return_value = 50.0
    nativo.getPinNumber.return_value = 18
    nativo.isActive.return_value = True
    assert (pino.duty, pino.frequency, pino.number, pino.active) == (0.25, 50.0, 18, True)


def test_with_libera_o_pino(nativo_falso):
    with Pin(17, PinMode.DIGITAL_OUT):
        pass
    nativo_falso.Pin.return_value.release.assert_called_once()


# ---------- hardware (Raspberry Pi) ----------

_TEST_PIN = os.environ.get("ROVER_TEST_PIN")


@pytest.mark.hardware
@pytest.mark.skipif(not _TEST_PIN, reason="defina ROVER_TEST_PIN com um pino BCM livre (nada ligado a ele)")
def test_hardware_saida_digital():
    assert pin_module.HARDWARE_AVAILABLE, "módulo nativo não carregou nesta Raspberry Pi"
    with Pin(int(_TEST_PIN), PinMode.DIGITAL_OUT) as pino:
        assert pino.active
        assert pino.number == int(_TEST_PIN)
        pino.on()
        pino.off()


@pytest.mark.hardware
@pytest.mark.skipif(not _TEST_PIN, reason="defina ROVER_TEST_PIN com um pino BCM livre (nada ligado a ele)")
def test_hardware_pwm_software():
    with Pin(int(_TEST_PIN), PinMode.DIGITAL_OUT) as pino:
        pino.pwm(0.5, 100)
        assert pino.duty == pytest.approx(0.5)
        assert pino.frequency == pytest.approx(100)
        pino.stop_pwm()
