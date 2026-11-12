"""
Testes da escolha automática de câmera (open_camera), sem hardware.

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/camera/tests
"""
import numpy as np
import pytest

from roverlib.plugins.camera import camera as camera_module
from roverlib.plugins.camera import factory, webcam
from roverlib.plugins.camera.factory import open_camera
from roverlib.plugins.camera.webcam import Webcam


class FakeVideoCapture:
    def __init__(self, index):
        self.index = index
        self.props = {}
        self.opened = True

    def set(self, prop, value):
        self.props[prop] = value

    def read(self):
        h = int(self.props.get(webcam.openCv.CAP_PROP_FRAME_HEIGHT, 480))
        w = int(self.props.get(webcam.openCv.CAP_PROP_FRAME_WIDTH, 640))
        return True, np.zeros((h, w, 3), dtype=np.uint8)

    def isOpened(self):
        return self.opened

    def release(self):
        self.opened = False


@pytest.fixture(autouse=True)
def webcam_falsa(monkeypatch):
    monkeypatch.setattr(webcam.openCv, "VideoCapture", FakeVideoCapture)


def test_sem_picamera_usa_webcam(monkeypatch, capsys):
    monkeypatch.setattr(camera_module, "availablePicamera2", False)
    cam = open_camera(240, 320, fps=15, index=1)
    assert isinstance(cam, Webcam)
    assert "webcam" in capsys.readouterr().out
    assert cam.camera.index == 1
    assert cam.get_frame().shape == (240, 320, 3)
    frame, t = cam.get_frame_time()
    assert frame is not None and t > 0
    assert cam.isRunning()
    cam.cleanup()
    assert not cam.isRunning()


def test_use_webcam_true_forca_webcam(monkeypatch):
    monkeypatch.setattr(camera_module, "availablePicamera2", True)
    monkeypatch.setattr(camera_module, "availableLibcamera", True)
    assert isinstance(open_camera(use_webcam=True), Webcam)


def test_use_webcam_false_sem_picamera_da_erro(monkeypatch):
    monkeypatch.setattr(camera_module, "availablePicamera2", False)
    with pytest.raises(ModuleNotFoundError):
        open_camera(use_webcam=False)


def test_com_picamera_usa_camera_e_inicia(monkeypatch):
    criadas = []

    class FakeCamera:
        def __init__(self, height, width, **kwargs):
            self.args = (height, width, kwargs)
            self.started = False
            criadas.append(self)

        def start(self):
            self.started = True

    monkeypatch.setattr(camera_module, "availablePicamera2", True)
    monkeypatch.setattr(camera_module, "availableLibcamera", True)
    monkeypatch.setattr(factory, "Camera", FakeCamera)

    cam = open_camera(480, 640, fps=20, verticalFlip=True)
    assert cam is criadas[0]
    assert cam.started
    assert cam.args == (480, 640, {"fps": 20, "index": 0, "verticalFlip": True})
