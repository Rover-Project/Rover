#include "../include/pin.hpp"
#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>

void Pin::writeFile(const std::string& path, const std::string& value) {
    std::ofstream file(path);
    if (!file) {
        std::cerr << "Erro ao abrir " << path << "\n";
        return;
    }
    file << value;
}

std::string Pin::readFile(const std::string& path) {
    std::ifstream file(path);
    std::string value;
    file >> value;
    return value;
}

Pin::Pin(int pin, PinMode mode) {
    this->pinNumber = pin;
    this->mode = mode;

    gpioPath = "/sys/class/gpio/gpio" + std::to_string(pinNumber);

    // exportar pino
    writeFile("/sys/class/gpio/export", std::to_string(pinNumber));

    // espera o sistema criar o diretório
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // definir direção
    if (mode == OUTPUT) {
        writeFile(gpioPath + "/direction", "out");
    } else {
        writeFile(gpioPath + "/direction", "in");
    }
}

Pin::~Pin() {
    writeFile("/sys/class/gpio/unexport", std::to_string(pinNumber));
}

void Pin::write(int value) {
    if (mode != OUTPUT) {
        std::cerr << "Pino não é saída\n";
        return;
    }

    writeFile(gpioPath + "/value", std::to_string(value));
}

int Pin::read() {
    std::string val = readFile(gpioPath + "/value");
    return std::stoi(val);
}