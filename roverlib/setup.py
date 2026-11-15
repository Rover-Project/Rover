"""
Compila o módulo nativo do plugin pin (GPIO/PWM em C++ com pybind11) durante a instalação.

A configuração do pacote fica no pyproject.toml; este arquivo só declara a extensão em C++.

- Raspberry Pi (Linux ARM): o `pip install` compila o módulo para a versão de Python em uso.
- PC (Windows, macOS, Linux x86): a extensão não é compilada e a RoverLib funciona em modo simulação.
- A extensão é opcional: se a compilação falhar, a instalação continua (sem acesso à GPIO) e
  a RoverLib explica o motivo ao tentar usar um pino.

Variáveis de ambiente:
    ROVER_BUILD_NATIVE=1   compila em qualquer Linux (útil para testar a compilação no PC)
    ROVER_BUILD_NATIVE=0   nunca compila
"""
import os
import platform
import sys

from setuptools import setup

PIN_SRC = "src/roverlib/plugins/pin/src"
ARM_MACHINES = ("aarch64", "arm64", "armv7l", "armv6l")


def _should_build_native() -> bool:
    forced = os.environ.get("ROVER_BUILD_NATIVE")
    if forced is not None:
        return forced == "1" and sys.platform.startswith("linux")
    return sys.platform.startswith("linux") and platform.machine().lower() in ARM_MACHINES


ext_modules = []
if _should_build_native():
    from pybind11.setup_helpers import Pybind11Extension

    ext_modules.append(
        Pybind11Extension(
            "roverlib.plugins.pin._pin_native",
            sources=[f"{PIN_SRC}/src/pin.cpp", f"{PIN_SRC}/binds.cpp"],
            include_dirs=[f"{PIN_SRC}/includes"],
            cxx_std=17,
            extra_compile_args=["-O2", "-pthread"],
            extra_link_args=["-pthread"],
            optional=True,  # falha na compilação não impede a instalação
        )
    )

setup(ext_modules=ext_modules)
