"""
Formato de cor dos frames da câmera.

Os frames da Picamera2 (formato "RGB888") e da webcam (OpenCV) chegam em BGR, a ordem de
cores do OpenCV. Por padrão eles são entregues assim; `set_format()` pede outra ordem.
"""
from enum import IntEnum

import cv2 as openCV


class CameraFormat(IntEnum):
    """
    Formatos de cor em que a câmera pode entregar os frames.

    - `BGR`: padrão do OpenCV, sem conversão. Use com `cv2.imshow()` e com `ProcessingImage`.
    - `RGB`: ordem usada por bibliotecas como MediaPipe, PIL e Matplotlib.
    - `Gray`: tons de cinza (um canal só).
    - `HSV`: matiz, saturação e valor; útil para filtrar cores com `cv2.inRange()`.
    """
    BGR = 0
    RGB = 1
    Gray = 2
    HSV = 3


# Conversão do OpenCV a partir do frame em BGR
_CONVERSIONS = {
    CameraFormat.RGB: openCV.COLOR_BGR2RGB,
    CameraFormat.Gray: openCV.COLOR_BGR2GRAY,
    CameraFormat.HSV: openCV.COLOR_BGR2HSV,
}

_NAMES = {f.name.lower(): f for f in CameraFormat}


def parse_format(value):
    """
    Interpreta o formato pedido pelo usuário.

    Args:
        value (CameraFormat | str | None): um `CameraFormat`, um nome (`"bgr"`, `"rgb"`,
            `"gray"`, `"hsv"`, sem diferenciar maiúsculas) ou None (BGR, sem conversão).

    Returns:
        CameraFormat: o formato correspondente.

    Raises:
        ValueError: formato desconhecido.
    """
    if value is None:
        return CameraFormat.BGR
    if isinstance(value, CameraFormat):
        return value
    if isinstance(value, str) and value.lower() in _NAMES:
        return _NAMES[value.lower()]
    raise ValueError(
        f"Formato de cor inválido: {value!r}. Use CameraFormat.BGR, .RGB, .Gray ou .HSV "
        "(ou os nomes 'bgr', 'rgb', 'gray', 'hsv')."
    )


def convert_frame(frame, fmt: CameraFormat):
    """
    Converte um frame em BGR para o formato pedido.

    Args:
        frame (numpy.ndarray | None): frame em BGR. None é devolvido como está.
        fmt (CameraFormat): formato desejado.

    Returns:
        numpy.ndarray | None: o frame convertido (o próprio frame, se o formato for BGR).
    """
    if frame is None or fmt == CameraFormat.BGR:
        return frame
    return openCV.cvtColor(frame, _CONVERSIONS[fmt])
