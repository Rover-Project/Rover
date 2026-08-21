"""
tests/test_driver.py
====================
Testes unitários para o driver PCA9685 e as classes de servo.

Execução:
    cd rover_pca9685
    python -m pytest tests/ -v

Os testes utilizam um mock do smbus2 para funcionar sem hardware físico.
"""

import sys
import os
import pytest

# ── Instala mock ANTES de qualquer import do projeto ──────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.mock_smbus2 import MockSMBus, install_mock

_mock_bus = install_mock()

# Agora importa normalmente
from pca9685.driver import (
    PCA9685Driver,
    I2CError,
    InvalidChannelError,
    InvalidFrequencyError,
    _REG_MODE1,
    _REG_PRE_SCALE,
    _REG_LED0_ON_L,
    _REG_ALL_LED_ON_L,
    _BIT_SLEEP,
)
from pca9685.servos import PCAServos, Servo, ContinuousServo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_mock_bus():
    """Limpa o estado do mock entre cada teste."""
    _mock_bus._registers.clear()
    _mock_bus.write_calls.clear()
    _mock_bus.read_calls.clear()
    yield


@pytest.fixture
def driver():
    return PCA9685Driver(address=0x40, bus=1)


@pytest.fixture
def pca():
    return PCAServos(address=0x40, bus=1, frequency=50)


# ---------------------------------------------------------------------------
# Testes: PCA9685Driver – inicialização
# ---------------------------------------------------------------------------
class TestDriverInit:
    def test_driver_cria_sem_excecao(self, driver):
        assert driver is not None

    def test_driver_endereco_padrao(self, driver):
        assert driver.address == 0x40

    def test_driver_escreve_mode1_no_reset(self):
        """O reset deve escrever em MODE1 ao menos 2 vezes."""
        d = PCA9685Driver()
        writes_to_mode1 = [c for c in _mock_bus.write_calls if c[1] == _REG_MODE1]
        assert len(writes_to_mode1) >= 2

    def test_repr_contem_endereco(self, driver):
        assert "0x40" in repr(driver)


# ---------------------------------------------------------------------------
# Testes: PCA9685Driver – frequência
# ---------------------------------------------------------------------------
class TestDriverFrequency:
    def test_set_frequency_50hz(self, driver):
        driver.set_frequency(50)
        # prescale esperado: round(25_000_000 / (4096 * 50)) - 1 = 121
        prescale_writes = [
            c for c in _mock_bus.write_calls if c[1] == _REG_PRE_SCALE
        ]
        assert len(prescale_writes) >= 1
        assert prescale_writes[-1][2] == 121

    def test_set_frequency_100hz(self, driver):
        driver.set_frequency(100)
        # prescale esperado: round(25_000_000 / (4096 * 100)) - 1 = 60
        prescale_writes = [
            c for c in _mock_bus.write_calls if c[1] == _REG_PRE_SCALE
        ]
        assert prescale_writes[-1][2] == 60

    def test_get_frequency_retorna_valor(self, driver):
        driver.set_frequency(50)
        assert driver.get_frequency() == 50

    def test_frequencia_invalida_abaixo(self, driver):
        with pytest.raises(InvalidFrequencyError):
            driver.set_frequency(10)

    def test_frequencia_invalida_acima(self, driver):
        with pytest.raises(InvalidFrequencyError):
            driver.set_frequency(2000)

    def test_set_frequency_entra_em_sleep(self, driver):
        """Durante set_frequency, MODE1 deve receber valor com BIT_SLEEP."""
        driver.set_frequency(50)
        sleep_writes = [
            c for c in _mock_bus.write_calls
            if c[1] == _REG_MODE1 and (c[2] & _BIT_SLEEP)
        ]
        assert len(sleep_writes) >= 1


# ---------------------------------------------------------------------------
# Testes: PCA9685Driver – controle de canais
# ---------------------------------------------------------------------------
class TestDriverChannels:
    def test_set_pwm_escreve_4_bytes(self, driver):
        _mock_bus.write_calls.clear()
        driver.set_pwm(0, 0, 307)
        reg_writes = [c for c in _mock_bus.write_calls]
        # 4 registradores: ON_L, ON_H, OFF_L, OFF_H
        assert len(reg_writes) == 4

    def test_set_pwm_registradores_corretos_canal0(self, driver):
        driver.set_pwm(0, 0, 307)
        base = _REG_LED0_ON_L  # 0x06
        regs = {c[1]: c[2] for c in _mock_bus.write_calls}
        assert regs[base + 0] == (0   & 0xFF)       # ON_L
        assert regs[base + 1] == (0   >> 8) & 0x0F  # ON_H
        assert regs[base + 2] == (307 & 0xFF)        # OFF_L
        assert regs[base + 3] == (307 >> 8) & 0x0F  # OFF_H

    def test_set_pwm_canal_diferente_calcula_offset(self, driver):
        driver.set_pwm(4, 0, 200)
        base = _REG_LED0_ON_L + 4 * 4  # 0x06 + 16 = 0x16
        regs = {c[1]: c[2] for c in _mock_bus.write_calls}
        assert base in regs

    def test_set_duty_cycle(self, driver):
        """set_duty_cycle(ch, v) deve resultar nos mesmos 4 registradores que set_pwm(ch, 0, v)."""
        _mock_bus.write_calls.clear()
        driver.set_pwm(0, 0, 500)
        expected = [(c[1], c[2]) for c in _mock_bus.write_calls]

        _mock_bus.write_calls.clear()
        driver.set_duty_cycle(0, 500)
        actual = [(c[1], c[2]) for c in _mock_bus.write_calls]
        assert expected == actual

    def test_set_duty_cycle_percent(self, driver):
        """7.5% de 4096 deve resultar em tick ≈ 307."""
        driver.set_duty_cycle_percent(0, 7.5)
        regs = {c[1]: c[2] for c in _mock_bus.write_calls}
        off_l = regs[_REG_LED0_ON_L + 2]
        off_h = regs[_REG_LED0_ON_L + 3]
        tick  = off_l | (off_h << 8)
        assert 305 <= tick <= 309  # tolerância ±2

    def test_canal_invalido_negativo(self, driver):
        with pytest.raises(InvalidChannelError):
            driver.set_pwm(-1, 0, 100)

    def test_canal_invalido_acima_de_15(self, driver):
        with pytest.raises(InvalidChannelError):
            driver.set_pwm(16, 0, 100)

    def test_set_all_pwm_usa_registradores_all(self, driver):
        _mock_bus.write_calls.clear()
        driver.set_all_pwm(0, 307)
        regs = {c[1] for c in _mock_bus.write_calls}
        assert _REG_ALL_LED_ON_L in regs

    def test_get_pwm_retorna_on_off(self, driver):
        driver.set_pwm(0, 0, 307)
        on, off = driver.get_pwm(0)
        assert on  == 0
        assert off == 307

    def test_reset_channel(self, driver):
        driver.set_pwm(0, 100, 300)
        driver.reset_channel(0)
        on, off = driver.get_pwm(0)
        assert on == 0 and off == 0


# ---------------------------------------------------------------------------
# Testes: PCAServos
# ---------------------------------------------------------------------------
class TestPCAServos:
    def test_pca_cria_sem_excecao(self, pca):
        assert pca is not None

    def test_set_pwm_delegado_ao_driver(self, pca):
        _mock_bus.write_calls.clear()
        pca.set_pwm(0, 0, 307)
        assert len(_mock_bus.write_calls) == 4

    def test_set_pulse_us_converte_para_tick(self, pca):
        """1500 µs a 50 Hz → tick = round(1500/20000*4096) = 307."""
        _mock_bus.write_calls.clear()
        pca.set_pulse_us(0, 1500)
        regs = {c[1]: c[2] for c in _mock_bus.write_calls}
        off_l = regs[_REG_LED0_ON_L + 2]
        off_h = regs[_REG_LED0_ON_L + 3]
        tick  = off_l | (off_h << 8)
        assert 305 <= tick <= 309

    def test_context_manager(self):
        with PCAServos() as pca:
            pca.set_pwm(0, 0, 307)
        # Sem exceção = OK


# ---------------------------------------------------------------------------
# Testes: Servo (0°–180°)
# ---------------------------------------------------------------------------
class TestServo:
    def test_angulo_0_graus(self, pca):
        s = Servo(pca, channel=0)
        s.angle = 0
        on, off = pca.get_pwm(0)
        # 0° → 500 µs → tick = round(500/20000*4096) = 102
        assert 100 <= off <= 104

    def test_angulo_180_graus(self, pca):
        s = Servo(pca, channel=0)
        s.angle = 180
        on, off = pca.get_pwm(0)
        # 180° → 2500 µs → tick = round(2500/20000*4096) = 512
        assert 510 <= off <= 514

    def test_angulo_90_graus(self, pca):
        s = Servo(pca, channel=0)
        s.angle = 90
        on, off = pca.get_pwm(0)
        # 90° → 1500 µs → tick ≈ 307
        assert 305 <= off <= 309

    def test_angulo_clampado_abaixo(self, pca):
        s = Servo(pca, channel=0)
        s.angle = -50
        assert s.angle == 0.0

    def test_angulo_clampado_acima(self, pca):
        s = Servo(pca, channel=0)
        s.angle = 250
        assert s.angle == 180.0

    def test_center(self, pca):
        s = Servo(pca, channel=0)
        s.center()
        assert s.angle == 90.0

    def test_detach_zera_canal(self, pca):
        s = Servo(pca, channel=0)
        s.angle = 90
        s.detach()
        on, off = pca.get_pwm(0)
        assert on == 0 and off == 0
        assert s.angle is None

    def test_canal_invalido(self, pca):
        with pytest.raises(InvalidChannelError):
            Servo(pca, channel=16)

    def test_repr(self, pca):
        s = Servo(pca, channel=2)
        assert "channel=2" in repr(s)


# ---------------------------------------------------------------------------
# Testes: ContinuousServo (360°)
# ---------------------------------------------------------------------------
class TestContinuousServo:
    def test_throttle_zero_neutro(self, pca):
        cs = ContinuousServo(pca, channel=1)
        cs.throttle = 0.0
        on, off = pca.get_pwm(1)
        # 0.0 → 1500 µs → tick ≈ 307
        assert 305 <= off <= 309

    def test_throttle_maximo_positivo(self, pca):
        cs = ContinuousServo(pca, channel=1)
        cs.throttle = 1.0
        on, off = pca.get_pwm(1)
        # +1.0 → 2500 µs → tick ≈ 512
        assert 510 <= off <= 514

    def test_throttle_maximo_negativo(self, pca):
        cs = ContinuousServo(pca, channel=1)
        cs.throttle = -1.0
        on, off = pca.get_pwm(1)
        # -1.0 → 500 µs → tick ≈ 102
        assert 100 <= off <= 104

    def test_throttle_clampado(self, pca):
        cs = ContinuousServo(pca, channel=1)
        cs.throttle = 5.0
        assert cs.throttle == 1.0

    def test_stop(self, pca):
        cs = ContinuousServo(pca, channel=1)
        cs.throttle = 1.0
        cs.stop()
        assert cs.throttle == 0.0

    def test_repr(self, pca):
        cs = ContinuousServo(pca, channel=3)
        assert "channel=3" in repr(cs)
