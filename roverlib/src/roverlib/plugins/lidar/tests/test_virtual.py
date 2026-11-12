"""
Testes do VirtualLidar e da API pública do plugin lidar.

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/lidar
"""
import pytest

from roverlib.exceptions import RoverLibError, HardwareNotAvailable
from roverlib.plugins import lidar as lidar_package
from roverlib.plugins.lidar import (
    VirtualLidar, LidarNotStart, LidarDoNotRespond, LidarNotAvailable,
)


def test_api_publica_do_pacote():
    assert {"Lidar", "VirtualLidar", "HARDWARE_AVAILABLE"} <= set(lidar_package.__all__)


def test_excecoes_compativeis():
    assert issubclass(LidarNotStart, RuntimeError) and issubclass(LidarNotStart, RoverLibError)
    assert issubclass(LidarDoNotRespond, RuntimeError) and issubclass(LidarDoNotRespond, RoverLibError)
    assert issubclass(LidarNotAvailable, ModuleNotFoundError)   # antes era ModuleNotFoundError
    assert issubclass(LidarNotAvailable, HardwareNotAvailable)


def test_mesma_interface_do_lidar_real():
    from roverlib.plugins.lidar import Lidar
    publicos = {"start", "stop", "is_open", "get_read", "get_distance", "is_obstacle"}
    assert publicos <= set(dir(Lidar)) and publicos <= set(dir(VirtualLidar))


def test_leituras():
    with VirtualLidar(distance=120, verbose=False) as lidar:
        assert lidar.is_open()
        assert lidar.get_read() == (120, 1000, 30.0)
        assert lidar.get_distance("m") == pytest.approx(1.2)
        assert not lidar.is_obstacle(30)
        lidar.set_distance(20)
        assert lidar.is_obstacle(30)
    assert not lidar.is_open()


def test_sinal_fraco_e_invalido():
    lidar = VirtualLidar(distance=50, verbose=False)
    lidar.start()
    lidar.set_distance(50, strength=40)
    assert lidar.get_distance() is None
    assert not lidar.is_obstacle(100)


def test_sem_start_gera_erro():
    with pytest.raises(LidarNotStart):
        VirtualLidar(verbose=False).get_read()


def test_aceita_opcoes_do_lidar_real():
    VirtualLidar(port="/dev/ttyAMA0", baudrate=115200, verbose=False)


def test_unidade_invalida():
    lidar = VirtualLidar(verbose=False)
    lidar.start()
    with pytest.raises(ValueError):
        lidar.get_distance("pol")
