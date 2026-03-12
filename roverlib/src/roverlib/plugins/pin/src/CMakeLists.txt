cmake_minimum_required(VERSION 3.15)

project(pin)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)

pybind11_add_module(pin
    binds.cpp
    src/pin.cpp
)

target_include_directories(pin PRIVATE includes)

set_target_properties(pin PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../bin
)
