#include "../includes/pin.hpp"
#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <filesystem>
#include <stdexcept>

// Função auxiliar para rodar comandos de sistema (pinctrl)
void Pin::setupHardwareMux(int pin, PinMode mode) {
    std::string command;
    if (mode == PWM) {
        command = "pinctrl set " + std::to_string(pin) + " a3";
    } else {
        command = "pinctrl set " + std::to_string(pin) + " op";
    }
    system(command.c_str());
}

bool Pin::pathExists(const std::string& path) {
    return std::filesystem::exists(path);
}

void Pin::validatePin(int pin) {
    if(pin < 0 || pin > 27)
        throw std::runtime_error("GPIO invalido: 0-27");
}

bool Pin::isPWMPin(int pin) {
    return (pin == 12 || pin == 13 || pin == 18 || pin == 19);
}

int Pin::gpioToPWMChannel(int pin) {
    if(pin == 12 || pin == 18) return 0;
    if(pin == 13 || pin == 19) return 1;
    throw std::runtime_error("GPIO nao suporta PWM");
}

void Pin::writeFile(const std::string& path, const std::string& value) {
    std::ofstream file(path);
    if(!file.is_open())
        throw std::runtime_error("Erro de I/O (verifique sudo): " + path);
    file << value;
    file.flush();
}

Pin::Pin(int pin, PinMode mode) {
    validatePin(pin);
    this->pinNumber = pin;
    this->mode = mode;
    this->active = false;

    // Configura o multiplexador do chip RP1 da Pi 5
    setupHardwareMux(pin, mode);

    if(mode == PWM) {
        pwmChannel = gpioToPWMChannel(pin);
        pwmPath = "/sys/class/pwm/pwmchip0/pwm" + std::to_string(pwmChannel);

        if(!pathExists(pwmPath)) {
            writeFile("/sys/class/pwm/pwmchip0/export", std::to_string(pwmChannel));
            std::this_thread::sleep_for(std::chrono::milliseconds(300));
        }

        // ORDEM CRÍTICA PARA EVITAR I/O ERROR:
        writeFile(pwmPath + "/enable", "0");
        writeFile(pwmPath + "/period", "1000000"); // 1ms (1kHz)
        writeFile(pwmPath + "/duty_cycle", "0");
        
        active = true;
        return;
    }

    // Lógica Digital Normal (BCM para Kernel 6.x)
    int kernelPin = pin + 571; 
    gpioPath = "/sys/class/gpio/gpio" + std::to_string(kernelPin);

    if(!pathExists(gpioPath)) {
        writeFile("/sys/class/gpio/export", std::to_string(kernelPin));
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    writeFile(gpioPath + "/direction", (mode == DIGITAL_OUT) ? "out" : "in");
    active = true;
}

void Pin::pwmWrite(float duty) {
    if(!active || mode != PWM) throw std::runtime_error("Erro no PWM");
    
    if(duty < 0.0) duty = 0.0;
    if(duty > 1.0) duty = 1.0;

    long period = 1000000;
    long dutyNs = static_cast<long>(period * duty);

    // Na Pi 5, o kernel prefere que você desative antes de mudar o duty pesado
    writeFile(pwmPath + "/enable", "0");
    writeFile(pwmPath + "/duty_cycle", std::to_string(dutyNs));
    writeFile(pwmPath + "/enable", "1");
}

void Pin::release() {
    if(!active) return;
    if(mode == PWM) {
        writeFile(pwmPath + "/enable", "0");
        writeFile("/sys/class/pwm/pwmchip0/unexport", std::to_string(pwmChannel));
    }
    active = false;
}

Pin::~Pin() { release(); }