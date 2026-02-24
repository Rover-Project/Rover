cmake_minimum_required(VERSION 4.1.2)

project(pin)

set(PIN_LIB pin_lib)

add_executable(${PROJECT_NAME} src/testLed.cpp)
add_library(${PIN_LIB})

target_sources(
    ${PIN_LIB}
    PRIVATE
        src/pin.cpp

    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES

            include/pin.hpp
)

target_link_libraries(${PROJECT_NAME} PRIVATE ${PIN_LIB})

set_target_properties(
    ${PROJECT_NAME} PROPERTIES

    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
)