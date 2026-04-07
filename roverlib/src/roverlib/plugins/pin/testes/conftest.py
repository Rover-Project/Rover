"""
conftest.py — executado automaticamente pelo Python antes de qualquer teste.

Adiciona o diretório pai (plugins/) ao sys.path para que
'from pin.pin import Pin, PinMode' funcione de dentro de pin/testes/.
"""
import sys
import os

# pin/testes/../  →  plugins/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))