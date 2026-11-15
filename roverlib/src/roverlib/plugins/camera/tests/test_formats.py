"""
Testes do formato de cor dos frames (CameraFormat / set_format), sem hardware.

Executar (na pasta roverlib/):  python -m pytest src/roverlib/plugins/camera
"""
from unittest.mock import MagicMock

import numpy as np
import pytest

from roverlib.plugins.camera import Webcam, CameraFormat
from roverlib.plugins.camera import webcam as webcam_module
from roverlib.plugins.camera.formats import convert_frame, parse_format

# Um pixel vermelho em BGR: azul=0, verde=0, vermelho=255
VERMELHO_BGR = np.zeros((2, 2, 3), np.uint8)
VERMELHO_BGR[:, :] = (0, 0, 255)


def test_bgr_e_o_padrao_e_nao_converte():
    assert parse_format(None) is CameraFormat.BGR
    assert convert_frame(VERMELHO_BGR, CameraFormat.BGR) is VERMELHO_BGR


def test_rgb_inverte_os_canais():
    rgb = convert_frame(VERMELHO_BGR, CameraFormat.RGB)
    assert tuple(rgb[0, 0]) == (255, 0, 0)


def test_gray_tem_um_canal():
    assert convert_frame(VERMELHO_BGR, CameraFormat.Gray).shape == (2, 2)


def test_hsv_do_vermelho_tem_matiz_zero():
    h, s, v = convert_frame(VERMELHO_BGR, CameraFormat.HSV)[0, 0]
    assert (h, s, v) == (0, 255, 255)


@pytest.mark.parametrize("nome, esperado", [("rgb", CameraFormat.RGB), ("GRAY", CameraFormat.Gray),
                                            ("Hsv", CameraFormat.HSV), (CameraFormat.BGR, CameraFormat.BGR)])
def test_aceita_nomes_e_enum(nome, esperado):
    assert parse_format(nome) is esperado


@pytest.mark.parametrize("invalido", ["yuv", 7, 3.5])
def test_formato_invalido_gera_erro_claro(invalido):
    with pytest.raises(ValueError, match="Formato de cor inválido"):
        parse_format(invalido)


def test_frame_none_continua_none():
    assert convert_frame(None, CameraFormat.RGB) is None


@pytest.fixture
def webcam_falsa(monkeypatch):
    captura = MagicMock()
    captura.read.return_value = (True, VERMELHO_BGR.copy())
    monkeypatch.setattr(webcam_module.openCv, "VideoCapture", MagicMock(return_value=captura))
    return Webcam(480, 640)


def test_webcam_aplica_set_format(webcam_falsa):
    assert tuple(webcam_falsa.get_frame()[0, 0]) == (0, 0, 255)      # BGR por padrão
    webcam_falsa.set_format("rgb")
    assert tuple(webcam_falsa.get_frame()[0, 0]) == (255, 0, 0)
    webcam_falsa.set_format(None)
    assert tuple(webcam_falsa.get_frame()[0, 0]) == (0, 0, 255)


def test_camera_aplica_o_formato_no_get_frame(monkeypatch):
    # A Camera real exige a Picamera2; aqui só o objeto da Picamera2 é simulado
    from roverlib.plugins.camera.camera import Camera
    cam = Camera.__new__(Camera)
    cam.runing = True
    cam.region_interest = None
    cam.picam2 = MagicMock()
    cam.picam2.capture_array.return_value = VERMELHO_BGR.copy()
    cam.set_format(CameraFormat.HSV)
    assert tuple(cam.get_frame()[0, 0]) == (0, 255, 255)
