"""
Testes da classe Rover (ponto de entrada único), sem hardware.

Executar (na pasta roverlib/):  python -m pytest src/roverlib/tests
"""
import textwrap

import pytest

import roverlib
from roverlib import rover as rover_module
from roverlib.rover import Rover, ComponentNotAvailable
from roverlib.modules.movement import robot as robot_module


class FakeCamera:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.brightness = None
        self.cleaned = False

    def set_brightness(self, value):
        self.brightness = value

    def cleanup(self):
        self.cleaned = True


class FakeLidar:
    def __init__(self, port="/dev/ttyAMA0", baudrate=115200):
        self.port = port
        self.started = False

    def start(self):
        self.started = True

    def stop(self):
        self.started = False


@pytest.fixture(autouse=True)
def sem_hardware(monkeypatch):
    """Motores sempre simulados e silenciosos; câmera e Lidar falsos."""
    monkeypatch.setattr(robot_module.time, "sleep", lambda s: None)
    monkeypatch.setenv(robot_module.SIMULATE_ENV, "1")

    from roverlib.plugins.camera import factory
    from roverlib.plugins.lidar import lidar

    monkeypatch.setattr(factory, "open_camera", lambda **kw: FakeCamera(**kw))
    monkeypatch.setattr(lidar, "Lidar", FakeLidar)
    monkeypatch.setattr(lidar, "availableSerial", True)


def escrever_config(tmp_path, texto):
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(texto), encoding="utf-8")
    return path


# ---------- from_config ----------

def test_config_completo(tmp_path):
    path = escrever_config(tmp_path, """
        motors:
          right: [1, 2]
          left: [3, 4]
          calibration: {right: 0.9, left: 1}
        camera:
          width: 320
          height: 240
          fps: 15
          brightness: 0.2
          vertical_flip: true
        lidar:
          port: /dev/ttyUSB0
          simulate: false
    """)
    with Rover.from_config(path) as rover:
        assert rover.simulated
        assert (rover.move.right_motor.in1, rover.move.right_motor.in2) == (1, 2)
        assert (rover.move.left_motor.in1, rover.move.left_motor.in2) == (3, 4)
        assert rover.move.calibration.right == 0.9

        assert rover.camera.kwargs["height"] == 240
        assert rover.camera.kwargs["width"] == 320
        assert rover.camera.kwargs["fps"] == 15
        assert rover.camera.kwargs["verticalFlip"] is True
        assert rover.camera.kwargs["use_webcam"] is None  # auto
        assert rover.camera.brightness == 0.2

        assert rover.lidar.port == "/dev/ttyUSB0"
        assert rover.lidar.started

        camera, lidar = rover.camera, rover.lidar
    assert camera.cleaned
    assert not lidar.started


def test_secoes_vazias_usam_padroes(tmp_path):
    path = escrever_config(tmp_path, """
        motors:
        camera:
    """)
    rover = Rover.from_config(path)
    assert (rover.move.right_motor.in1, rover.move.right_motor.in2) == rover_module.DEFAULT_RIGHT_PINS
    assert rover.camera.kwargs["height"] == 480
    assert not rover.has("lidar")


def test_compatibilidade_com_gpio_motor(tmp_path):
    path = escrever_config(tmp_path, """
        gpio:
          motor:
            right: [17, 26]
            left: [25, 16]
            calibration: {right: 1, left: 0.8}
    """)
    rover = Rover.from_config(path)
    assert rover.move.calibration.left == 0.8


def test_arquivo_vazio_nao_cria_componentes(tmp_path):
    rover = Rover.from_config(escrever_config(tmp_path, ""))
    assert repr(rover) == "Rover(sem componentes)"
    assert rover.simulated is False


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        Rover.from_config(tmp_path / "nao_existe.yaml")


def test_simulate_e_webcam_explicitos(tmp_path, monkeypatch):
    monkeypatch.delenv(robot_module.SIMULATE_ENV)
    path = escrever_config(tmp_path, """
        motors:
          simulate: true
        camera:
          webcam: true
    """)
    rover = Rover.from_config(path)
    assert rover.simulated
    assert rover.camera.kwargs["use_webcam"] is True


# ---------- componentes indisponíveis ----------

def test_componente_nao_configurado_explica_o_que_falta():
    rover = Rover(motors={})
    with pytest.raises(ComponentNotAvailable, match="camera:"):
        rover.camera
    with pytest.raises(ComponentNotAvailable, match="lidar:"):
        rover.lidar
    assert rover.has("move") and not rover.has("camera")


def test_falha_em_componente_opcional_nao_derruba_o_rover(monkeypatch, capsys):
    from roverlib.plugins.lidar import lidar

    class LidarQuebrado(FakeLidar):
        def start(self):
            raise RuntimeError("porta serial não encontrada")

    monkeypatch.setattr(lidar, "Lidar", LidarQuebrado)
    rover = Rover(motors={}, lidar={"simulate": False})
    assert "lidar não pôde ser iniciado" in capsys.readouterr().out
    rover.move.forward(30)  # o resto continua funcionando
    with pytest.raises(ComponentNotAvailable, match="porta serial"):
        rover.lidar


def test_stop_e_cleanup_repetido():
    rover = Rover(motors={}, camera={}, lidar={})
    rover.move.forward(50)
    rover.stop()
    assert rover.move.left_motor.direction == "STOP"
    rover.cleanup()
    rover.cleanup()


# ---------- pan-tilt ----------

def test_pan_tilt_pelo_config(tmp_path, monkeypatch):
    from roverlib.modules.pan_tilt import pan_tilt as pt_module
    monkeypatch.setattr(pt_module.time, "sleep", lambda s: None)
    path = escrever_config(tmp_path, """
        pan_tilt:
          address: 0x41
          pan:
            channel: 2
            trim: 0.03
            invert: true
            time_per_turn: 3.5
          tilt:
            channel: 3
            min: 40
            max: 140
            center: 85
    """)
    with Rover.from_config(path) as rover:
        pt = rover.pan_tilt
        assert pt.simulated                    # ROVER_SIMULATE=1 na fixture
        assert pt._pan._channel == 2 and pt._tilt._channel == 3
        assert (pt.pan_trim, pt.pan_invert, pt.pan_time_per_turn) == (0.03, True, 3.5)
        assert (pt.tilt_min, pt.tilt_max, pt.tilt_center) == (40, 140, 85)
        pt.pan_right(50)
        rover.stop()                           # stop() também para o PAN
        assert pt.pan_speed == 0
        assert "pan-tilt simulado" in repr(rover)


def test_pan_tilt_secao_vazia_usa_padroes(tmp_path):
    rover = Rover.from_config(escrever_config(tmp_path, "pan_tilt:"))
    assert rover.pan_tilt._pan._channel == 0
    assert rover.pan_tilt._tilt._channel == 1
    with pytest.raises(ComponentNotAvailable, match="motors:"):
        rover.move


# ---------- atalhos do pacote ----------

def test_atalhos_do_pacote():
    assert roverlib.Rover is Rover
    from roverlib import Robot, PID, open_camera, Lidar, PanTilt, ProcessingImage, VisionModule  # noqa: F401
    with pytest.raises(AttributeError):
        roverlib.NaoExiste


# ---------- Lidar simulado ----------

def test_lidar_simulado_por_padrao_no_pc(tmp_path):
    from roverlib.plugins.lidar import VirtualLidar
    path = escrever_config(tmp_path, """
        lidar:
          simulated_distance: 25
    """)
    with Rover.from_config(path) as rover:
        assert isinstance(rover.lidar, VirtualLidar)
        assert rover.lidar.get_distance() == 25
        assert rover.lidar.is_obstacle(30)
        rover.lidar.set_distance(150)
        assert not rover.lidar.is_obstacle(30)


def test_lidar_auto_sem_porta_simula(monkeypatch, capsys):
    from roverlib.plugins.lidar import VirtualLidar
    monkeypatch.delenv(robot_module.SIMULATE_ENV)
    rover = Rover(lidar={"port": "/dev/porta_que_nao_existe"})
    assert isinstance(rover.lidar, VirtualLidar)
    assert "Lidar simulado" in capsys.readouterr().out
