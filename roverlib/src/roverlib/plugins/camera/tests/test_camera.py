"""
Testes da API pública e das exceções do plugin camera (sem hardware).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/camera
"""
import pytest

from roverlib.exceptions import RoverLibError, HardwareNotAvailable
from roverlib.plugins import camera as camera_package
from roverlib.plugins.camera import camera as camera_module
from roverlib.plugins.camera import (
    Camera, AfCamera, AfModeEnum, AfSpeedEnum, Webcam, CameraInterface,
    CameraNotStart, AutofocusModeInvalid, CameraNotAvailable,
)


def test_api_publica_do_pacote():
    assert {"open_camera", "Camera", "AfCamera", "Webcam", "HARDWARE_AVAILABLE"} <= set(camera_package.__all__)
    assert issubclass(Camera, CameraInterface) and issubclass(Webcam, CameraInterface)
    assert issubclass(AfCamera, Camera)


def test_enums_de_foco_importaveis_no_pc():
    assert {m.name for m in AfModeEnum} == {"Manual", "Auto", "Continuous"}
    assert {m.name for m in AfSpeedEnum} == {"Normal", "Fast"}


def test_excecoes_compativeis():
    assert issubclass(CameraNotStart, RuntimeError) and issubclass(CameraNotStart, RoverLibError)
    assert issubclass(AutofocusModeInvalid, RuntimeError) and issubclass(AutofocusModeInvalid, RoverLibError)
    assert issubclass(CameraNotAvailable, ModuleNotFoundError)   # antes era ModuleNotFoundError
    assert issubclass(CameraNotAvailable, HardwareNotAvailable)


@pytest.mark.parametrize("classe", [Camera, AfCamera])
def test_sem_picamera_gera_camera_not_available(monkeypatch, classe):
    monkeypatch.setattr(camera_module, "availablePicamera2", False)
    with pytest.raises(CameraNotAvailable):
        classe(480, 640)
