
import sys as _sys
import os as _os

# Garante que o _pin_native.so seja encontrado independente de onde
# o pacote é importado dentro do projeto
_BIN_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bin")
if _BIN_DIR not in _sys.path:
    _sys.path.insert(0, _BIN_DIR)

from .pin import Pin
from .pin import PinMode

