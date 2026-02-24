cmake_minimum_required(VERSION 4.1.2)

project(pin)

add_library(${PROJECT_NAME})

target_sources(
    ${PROJECT_NAME}
    PRIVATE 
        src/pin.cpp

    PUBLIC 
        FILE_SET HEADERS
        BASE_DIRS include
        FILES 

            include/pin.hpp
)

set_target_properties(
    ${PROJECT_NAME} PROPERTIES

    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
)