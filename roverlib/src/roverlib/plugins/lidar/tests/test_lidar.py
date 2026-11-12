"""
Testes do plugin Lidar (TF-Luna) com uma porta serial simulada.
Não precisa do sensor nem do pyserial instalado.

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/lidar/tests
"""
import sys
import threading
import time
import types

import pytest


# ---------- porta serial falsa ----------

class FakeSerialException(Exception):
    pass


class FakeSerial:
    instances = []

    def __init__(self, port, baudrate, bytesize, parity, stopbits, timeout):
        self.buffer = bytearray()
        self.lock = threading.Lock()
        self.is_open = True
        self.out_waiting = 0
        self.settings = {"baudrate": baudrate, "timeout": timeout}
        FakeSerial.instances.append(self)

    @property
    def in_waiting(self):
        if not self.is_open:
            raise FakeSerialException("porta fechada")
        return len(self.buffer)

    def feed(self, data: bytes):
        with self.lock:
            self.buffer.extend(data)

    def read(self, n=1):
        if not self.is_open:
            raise FakeSerialException("porta fechada")
        with self.lock:
            out = bytes(self.buffer[:n])
            del self.buffer[:n]
            return out

    def reset_input_buffer(self):
        with self.lock:
            self.buffer.clear()

    def reset_output_buffer(self):
        pass

    def close(self):
        self.is_open = False

    def get_settings(self):
        return dict(self.settings)

    def apply_settings(self, d):
        self.settings = dict(d)


fake_serial = types.ModuleType("serial")
fake_serial.Serial = FakeSerial
fake_serial.SerialException = FakeSerialException
sys.modules["serial"] = fake_serial
sys.modules.pop("roverlib.plugins.lidar.lidar", None)

from roverlib.plugins.lidar.lidar import Lidar  # noqa: E402
from roverlib.plugins.lidar.exceptions import LidarNotStart, LidarDoNotRespond  # noqa: E402


def frame(dist, strength=1000, temp_c=30.0, corrupt=False):
    temp_raw = int((temp_c + 256) * 8)
    body = [0x59, 0x59, dist & 0xFF, dist >> 8, strength & 0xFF, strength >> 8,
            temp_raw & 0xFF, temp_raw >> 8]
    checksum = sum(body) & 0xFF
    if corrupt:
        checksum = (checksum + 1) & 0xFF
    return bytes(body + [checksum])


def wait_for(cond, timeout=1.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.005)
    return False


@pytest.fixture
def lidar():
    lid = Lidar()
    lid.start()
    yield lid
    lid.stop()


# ---------- testes ----------

def test_sem_leitura_retorna_valores_padrao(lidar):
    assert lidar.get_read() == (-1, -1, -1)
    assert lidar.get_distance() is None
    assert lidar.is_obstacle(30) is False


def test_decodifica_quadro(lidar):
    lidar.lidar.feed(frame(123, strength=900, temp_c=40.0))
    assert wait_for(lambda: lidar.get_read()[0] == 123)
    assert lidar.get_read() == (123, 900, 40.0)
    assert lidar.get_distance() == 123
    assert lidar.get_distance("m") == pytest.approx(1.23)
    assert lidar.get_distance("mm") == 1230


def test_sincroniza_com_lixo_antes_do_cabecalho(lidar):
    lidar.lidar.feed(b"\x01\x59\x02" + frame(77))
    assert wait_for(lambda: lidar.get_distance() == 77)


def test_descarta_quadro_com_checksum_invalido(lidar):
    lidar.lidar.feed(frame(50, corrupt=True) + frame(60))
    assert wait_for(lambda: lidar.get_distance() == 60)
    # o quadro corrompido (50) nunca deve ter sido aceito
    assert lidar.get_read()[0] == 60


def test_sinal_fraco_ou_saturado_nao_e_confiavel(lidar):
    lidar.lidar.feed(frame(40, strength=50))
    assert wait_for(lambda: lidar.get_read()[0] == 40)
    assert lidar.get_distance() is None
    assert lidar.is_obstacle(100) is False

    lidar.lidar.feed(frame(41, strength=65535))
    assert wait_for(lambda: lidar.get_read()[0] == 41)
    assert lidar.get_distance() is None


def test_is_obstacle(lidar):
    lidar.lidar.feed(frame(25))
    assert wait_for(lambda: lidar.get_distance() == 25)
    assert lidar.is_obstacle(30) is True
    assert lidar.is_obstacle(25) is True
    assert lidar.is_obstacle(20) is False


def test_unidade_invalida(lidar):
    with pytest.raises(ValueError):
        lidar.get_distance("pol")


def test_temperatura_critica_desliga_sem_erro(lidar):
    errors = []
    old_hook = threading.excepthook
    threading.excepthook = lambda args: errors.append(args.exc_value)
    try:
        lidar.lidar.feed(frame(100, temp_c=70.0))
        assert wait_for(lambda: not lidar.is_open())
        lidar._thread.join(timeout=1)
        assert not lidar._thread.is_alive()
        assert errors == []
    finally:
        threading.excepthook = old_hook


def test_stop_encerra_thread_e_fecha_porta():
    lid = Lidar()
    lid.start()
    lid.stop()
    assert not lid.is_open()
    assert not lid._thread.is_alive()
    lid.stop()  # chamar de novo não deve dar erro


def test_context_manager():
    with Lidar() as lid:
        assert lid.is_open()
    assert not lid.is_open()


def test_is_open_antes_de_start():
    assert Lidar().is_open() is False


def test_change_config(lidar):
    assert lidar.change_config()["timeout"] == 1
    assert lidar.change_config(timeout=2)["timeout"] == 2
    with pytest.raises(ValueError):
        lidar.change_config(nao_existe=1)


def test_change_config_sem_start():
    with pytest.raises(LidarNotStart):
        Lidar().change_config()


def test_get_reads_until():
    lid = Lidar()
    lid.start()
    lid.is_read_running = False  # para a thread não consumir os bytes
    lid._thread.join(timeout=1)
    lid.lidar.feed(b"abcdef")
    assert lid.get_reads_until(4) == b"abcd"
    lid.lidar.reset_input_buffer()
    with pytest.raises(LidarDoNotRespond):
        lid.get_reads_until(4)
    lid.stop()
