"""
_path.py — importe este módulo no topo de cada script de teste.

Garante que o pacote 'pin' seja encontrado independente de onde
o script é executado.

Uso:
    import _path  # noqa (deve ser o primeiro import)
    from pin.pin import Pin, PinMode
"""
import sys
import os

# Resolve: pin/testes/_path.py  →  sobe para plugins/
_PLUGINS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PLUGINS_DIR not in sys.path:
    sys.path.insert(0, _PLUGINS_DIR)