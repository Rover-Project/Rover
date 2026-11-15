"""
Plugin pin: controle de GPIO e PWM da Raspberry Pi por um módulo nativo em C++ (pybind11),
compilado durante o `pip install` na Raspberry Pi.

    from roverlib.plugins.pin import Pin, PinMode, HARDWARE_AVAILABLE
"""
from .pin import Pin, PinMode, HARDWARE_AVAILABLE, NATIVE_IMPORT_ERROR, gpio_base, is_raspberry_pi
from .exceptions import PinNotAvailable

__all__ = ["Pin", "PinMode", "HARDWARE_AVAILABLE", "NATIVE_IMPORT_ERROR", "PinNotAvailable",
           "gpio_base", "is_raspberry_pi"]
