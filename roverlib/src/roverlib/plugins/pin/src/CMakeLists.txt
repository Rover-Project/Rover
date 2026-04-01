cmake_minimum_required(VERSION 3.15)
project(pin VERSION 1.0.0 LANGUAGES CXX)

# ── Padrão C++ ────────────────────────────────────────────────────────────── #
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Flags de compilação ───────────────────────────────────────────────────── #
# -O2         → otimização segura para código embarcado
# -Wall       → todos os avisos principais
# -Wextra     → avisos extras
# -pthread    → suporte a threads (necessário para soft-PWM)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall -Wextra -pthread")

# ── pybind11 ──────────────────────────────────────────────────────────────── #
# Tenta encontrar pybind11 instalado via pip ou sistema.
# Caso não encontre, use: pip install pybind11
find_package(pybind11 REQUIRED)

# ── Módulo Python ─────────────────────────────────────────────────────────── #
pybind11_add_module(pin
    src/src/pin.cpp
    src/binds.cpp
)

# Headers da biblioteca
target_include_directories(pin PRIVATE src/includes)

# ── Destino de saída ──────────────────────────────────────────────────────── #
# O .so gerado vai direto para pin/bin/, onde pin.py o importa
set_target_properties(pin PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../bin"
)
