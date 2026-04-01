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
# Suprimir aviso de política CMP0148 (módulos FindPython legados)
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

# ── Módulo Python ─────────────────────────────────────────────────────────── #
# CMAKE_SOURCE_DIR = pin/src/  (onde este CMakeLists.txt está)
# Os arquivos fonte ficam em:
#   pin/src/src/pin.cpp
#   pin/src/binds.cpp
pybind11_add_module(_pin_native
    ${CMAKE_SOURCE_DIR}/src/pin.cpp
    ${CMAKE_SOURCE_DIR}/binds.cpp
)

# Headers ficam em pin/src/includes/
target_include_directories(_pin_native PRIVATE ${CMAKE_SOURCE_DIR}/includes)

set_target_properties(_pin_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../bin"
)