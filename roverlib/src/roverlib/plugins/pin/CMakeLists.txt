cmake_minimum_required(VERSION 3.14)
project(pin)

set(CMAKE_CXX_STANDARD 17)

# Encontra pybind11
find_package(pybind11 REQUIRED)

# Cria módulo Python
pybind11_add_module(pin
    src/bindings.cpp
    src/pin.cpp
)

target_include_directories(pin PRIVATE include)
