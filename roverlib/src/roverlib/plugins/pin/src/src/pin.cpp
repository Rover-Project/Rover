#include "../includes/pin.hpp"

#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <filesystem>
#include <stdexcept>

int bcmToKernel(int bcm)
{
    return bcm + 571;
}

bool Pin::pathExists(const std::string& path)
{
    return std::filesystem::exists(path);
}

void Pin::validatePin(int pin)
{
    if(pin < 0 || pin > 27)
        throw std::runtime_error("GPIO invalido: use valores entre 0 e 27");
}

bool Pin::isPWMPin(int pin)
{
    return (pin == 12 || pin == 13 || pin == 18 || pin == 19);
}

/* NOVO: mapeamento GPIO -> canal PWM */
int Pin::gpioToPWMChannel(int pin)
{
    if(pin == 12 || pin == 18)
        return 0;

    if(pin == 13 || pin == 19)
        return 1;

    throw std::runtime_error("GPIO nao suporta PWM");
}

void Pin::writeFile(const std::string& path, const std::string& value)
{
    std::ofstream file(path);

    if(!file.is_open())
        throw std::runtime_error("Nao foi possivel acessar: " + path);

    file << value;
    file.flush(); // FORÇA a escrita no disco/hardware imediatamente
    file.close(); // Garante o fechamento antes de sair da função
}

std::string Pin::readFile(const std::string& path)
{
    std::ifstream file(path);
    std::string value;

    if(!file.is_open())
        throw std::runtime_error("Nao foi possivel ler: " + path);

    file >> value;

    return value;
}

Pin::Pin(int pin, PinMode mode)
{
    validatePin(pin);

    pinNumber = pin;
    this->mode = mode;

    active = false;

    if(mode == PWM)
    {
        if(!isPWMPin(pin))
            throw std::runtime_error("Este pino nao suporta PWM");

        /* CORREÇÃO IMPORTANTE */
        pwmChannel = gpioToPWMChannel(pin);

        pwmPath = "/sys/class/pwm/pwmchip0/pwm" + std::to_string(pwmChannel);

        if(!pathExists(pwmPath))
        {
            writeFile("/sys/class/pwm/pwmchip0/export", std::to_string(pwmChannel));
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }

        writeFile(pwmPath + "/period", "20000000");

        active = true;

        return;
    }

    kernelPin = bcmToKernel(pin);

    gpioPath = "/sys/class/gpio/gpio" + std::to_string(kernelPin);

    if(!pathExists(gpioPath))
    {
        writeFile("/sys/class/gpio/export", std::to_string(kernelPin));
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    if(mode == DIGITAL_OUT)
        writeFile(gpioPath + "/direction", "out");
    else
        writeFile(gpioPath + "/direction", "in");

    active = true;
}

Pin::~Pin()
{
    release();
}

void Pin::release()
{
    if(!active)
        return;

    if(mode == PWM)
    {
        if(pathExists(pwmPath))
        {
            /* desliga antes de liberar */
            writeFile(pwmPath + "/enable", "0");

            writeFile("/sys/class/pwm/pwmchip0/unexport",
                      std::to_string(pwmChannel));
        }

        active = false;
        return;
    }

    // --- CORREÇÃO PARA MODO DIGITAL ---
    if(pathExists(gpioPath))
    {
        /* 1. Força o valor para 0 (OFF) antes de remover o pino */
        writeFile(gpioPath + "/value", "0");
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        /* 2. Agora sim, libera o pino do kernel */
        writeFile("/sys/class/gpio/unexport", std::to_string(kernelPin));
    }

    active = false;
}

void Pin::write(int value)
{
    if(!active)
        throw std::runtime_error("GPIO nao inicializado");

    if(mode != DIGITAL_OUT)
        throw std::runtime_error("Tentativa de escrita em pino nao OUTPUT");

    if(value != 0 && value != 1)
        throw std::runtime_error("Valor invalido (use 0 ou 1)");

    writeFile(gpioPath + "/value", std::to_string(value));
}

int Pin::read()
{
    if(!active)
        throw std::runtime_error("GPIO nao inicializado");

    if(mode != DIGITAL_IN)
        throw std::runtime_error("Tentativa de leitura em pino nao INPUT");

    std::string val = readFile(gpioPath + "/value");

    return std::stoi(val);
}

void Pin::pwmWrite(float duty)
{
    if(!active)
        throw std::runtime_error("PWM nao inicializado");

    if(mode != PWM)
        throw std::runtime_error("Pino nao configurado como PWM");

    if(duty < 0.0 || duty > 1.0)
        throw std::runtime_error("Duty cycle deve estar entre 0 e 1");

    int period = 20000000;

    int dutyCycle = period * duty;

    writeFile(pwmPath + "/duty_cycle", std::to_string(dutyCycle));

    writeFile(pwmPath + "/enable", "1");
}