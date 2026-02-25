#include "../include/pin.hpp"
#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>

int bcmToKernel(int bcm) {
    return bcm + 571;
}

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

    this->kernelPin = bcmToKernel(pinNumber);

    gpioPath = "/sys/class/gpio/gpio" + std::to_string(kernelPin);

    writeFile("/sys/class/gpio/export", std::to_string(kernelPin));

    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    if (mode == OUTPUT) {
        writeFile(gpioPath + "/direction", "out");
    } else {
        writeFile(gpioPath + "/direction", "in");
    }
}

Pin::~Pin() {
    writeFile("/sys/class/gpio/unexport", std::to_string(kernelPin));
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
    try {
        return std::stoi(val);
    } catch (...) {
        return -1;
    }
}