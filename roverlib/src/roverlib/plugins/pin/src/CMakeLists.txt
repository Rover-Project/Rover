cmake_minimum_required(VERSION 3.15)
project(pin VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall -Wextra -pthread")

# Forçar Python do sistema (3.13) antes do find_package
set(PYTHON_EXECUTABLE "/usr/bin/python3" CACHE FILEPATH "Python interpreter" FORCE)

find_package(pybind11 REQUIRED)

pybind11_add_module(_pin_native
    ${CMAKE_SOURCE_DIR}/src/pin.cpp
    ${CMAKE_SOURCE_DIR}/binds.cpp
)

target_include_directories(_pin_native PRIVATE ${CMAKE_SOURCE_DIR}/includes)

set_target_properties(_pin_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../bin"
)