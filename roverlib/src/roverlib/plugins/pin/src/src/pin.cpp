#include "../includes/pin.hpp"

#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <filesystem>
#include <stdexcept>
#include <cmath>

// ========================================================================== //
//  Utilitários estáticos                                                     //
// ========================================================================== //

int Pin::bcmToKernel(int bcm)
{
    // Offset padrão para Raspberry Pi 5; ajuste se usar RPi 4 (offset = 512)
    return bcm + 571;
}

bool Pin::pathExists(const std::string& path)
{
    return std::filesystem::exists(path);
}

void Pin::validatePin(int pin)
{
    if (pin < 0 || pin > 27)
        throw std::runtime_error(
            "GPIO invalido: " + std::to_string(pin) + ". Use valores entre 0 e 27.");
}

bool Pin::isPWMPin(int pin)
{
    return (pin == 12 || pin == 13 || pin == 18 || pin == 19);
}

int Pin::gpioToPWMChannel(int pin)
{
    if (pin == 12 || pin == 18) return 0;
    if (pin == 13 || pin == 19) return 1;
    throw std::runtime_error("GPIO " + std::to_string(pin) + " nao suporta PWM hardware.");
}

// ========================================================================== //
//  I/O de arquivos sysfs                                                      //
// ========================================================================== //

void Pin::writeFile(const std::string& path, const std::string& value)
{
    std::ofstream file(path);
    if (!file.is_open())
        throw std::runtime_error("Nao foi possivel escrever em: " + path);

    file << value;
    file.flush();
    file.close();
}

std::string Pin::readFile(const std::string& path)
{
    std::ifstream file(path);
    if (!file.is_open())
        throw std::runtime_error("Nao foi possivel ler: " + path);

    std::string value;
    file >> value;
    return value;
}

// ========================================================================== //
//  Construtor / Destrutor                                                     //
// ========================================================================== //

Pin::Pin(int pin, PinMode mode) : mode(mode)
{
    validatePin(pin);
    pinNumber = pin;

    // ---------------------------------------------------------------------- //
    //  Modo PWM por hardware                                                  //
    // ---------------------------------------------------------------------- //
    if (mode == PWM)
    {
        if (!isPWMPin(pin))
            throw std::runtime_error(
                "GPIO " + std::to_string(pin) + " nao suporta PWM hardware. "
                "Use os pinos 12, 13, 18 ou 19. "
                "Para outros pinos, use DIGITAL_OUT com pwmWrite().");

        pwmChannel = gpioToPWMChannel(pin);
        pwmPath    = "/sys/class/pwm/pwmchip0/pwm" + std::to_string(pwmChannel);

        if (!pathExists(pwmPath))
        {
            writeFile("/sys/class/pwm/pwmchip0/export", std::to_string(pwmChannel));
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }

        // Período inicial: 50 Hz → 20 000 000 ns
        long periodNs = static_cast<long>(1e9f / 50.0f);
        writeFile(pwmPath + "/period", std::to_string(periodNs));

        active = true;
        return;
    }

    // ---------------------------------------------------------------------- //
    //  Modo digital (IN ou OUT) — ou DIGITAL_OUT para soft-PWM               //
    // ---------------------------------------------------------------------- //
    kernelPin = bcmToKernel(pin);
    gpioPath  = "/sys/class/gpio/gpio" + std::to_string(kernelPin);

    if (!pathExists(gpioPath))
    {
        writeFile("/sys/class/gpio/export", std::to_string(kernelPin));
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    writeFile(gpioPath + "/direction", (mode == DIGITAL_OUT) ? "out" : "in");

    active = true;
}

Pin::~Pin()
{
    release();
}

// ========================================================================== //
//  Liberação de recursos                                                      //
// ========================================================================== //

void Pin::release()
{
    if (!active) return;

    stopSoftPwm();

    if (mode == PWM && isPWMPin(pinNumber))
    {
        if (pathExists(pwmPath))
        {
            writeFile(pwmPath + "/enable", "0");
            writeFile("/sys/class/pwm/pwmchip0/unexport", std::to_string(pwmChannel));
        }
    }
    else if (pathExists(gpioPath))
    {
        // Garante pino em LOW antes de liberar
        try { writeFile(gpioPath + "/value", "0"); } catch (...) {}
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        writeFile("/sys/class/gpio/unexport", std::to_string(kernelPin));
    }

    active = false;
}

// ========================================================================== //
//  Interface Digital                                                          //
// ========================================================================== //

void Pin::write(int value)
{
    if (!active)
        throw std::runtime_error("Pino nao inicializado.");

    if (mode != DIGITAL_OUT)
        throw std::runtime_error("write() requer modo DIGITAL_OUT.");

    if (value != 0 && value != 1)
        throw std::runtime_error("Valor invalido: use 0 ou 1.");

    std::lock_guard<std::mutex> lock(ioMutex);
    writeFile(gpioPath + "/value", std::to_string(value));
}

int Pin::read()
{
    if (!active)
        throw std::runtime_error("Pino nao inicializado.");

    if (mode != DIGITAL_IN)
        throw std::runtime_error("read() requer modo DIGITAL_IN.");

    std::lock_guard<std::mutex> lock(ioMutex);
    return std::stoi(readFile(gpioPath + "/value"));
}

// ========================================================================== //
//  Interface PWM                                                              //
// ========================================================================== //

void Pin::pwmWrite(float duty, float frequencyHz)
{
    if (!active)
        throw std::runtime_error("Pino nao inicializado.");

    if (duty < 0.0f || duty > 1.0f)
        throw std::runtime_error("duty deve estar entre 0.0 e 1.0.");

    if (frequencyHz <= 0.0f)
        throw std::runtime_error("frequencyHz deve ser maior que zero.");

    currentDuty.store(duty);
    currentFrequency.store(frequencyHz);

    // ---------------------------------------------------------------------- //
    //  Hardware PWM                                                           //
    // ---------------------------------------------------------------------- //
    if (mode == PWM && isPWMPin(pinNumber))
    {
        long periodNs   = static_cast<long>(1e9f / frequencyHz);
        long dutyCycleNs = static_cast<long>(periodNs * duty);

        // Ao alterar o período é obrigatório desabilitar, mudar e reabilitar
        writeFile(pwmPath + "/enable",     "0");
        writeFile(pwmPath + "/period",     std::to_string(periodNs));
        writeFile(pwmPath + "/duty_cycle", std::to_string(dutyCycleNs));
        writeFile(pwmPath + "/enable",     "1");
        return;
    }

    // ---------------------------------------------------------------------- //
    //  Software PWM (qualquer pino DIGITAL_OUT)                              //
    // ---------------------------------------------------------------------- //
    if (mode != DIGITAL_OUT)
        throw std::runtime_error(
            "pwmWrite() requer modo PWM ou DIGITAL_OUT.");

    if (!runSoftPwm)
        startSoftPwm();
    // A thread já lê currentDuty e currentFrequency atomicamente —
    // não é necessário reiniciá-la para mudar parâmetros em tempo real.
}

void Pin::pwmStop()
{
    if (!active) return;

    stopSoftPwm();

    if (mode == PWM && isPWMPin(pinNumber) && pathExists(pwmPath))
        writeFile(pwmPath + "/enable", "0");
}

// ========================================================================== //
//  Soft-PWM: implementação da thread                                         //
// ========================================================================== //

void Pin::startSoftPwm()
{
    runSoftPwm = true;
    writeFile(gpioPath + "/direction", "out"); // garante direção correta
    softPwmThread = std::thread(&Pin::softPwmWorker, this);
}

void Pin::stopSoftPwm()
{
    if (!runSoftPwm) return;

    runSoftPwm = false;
    if (softPwmThread.joinable())
        softPwmThread.join();

    // Deixa o pino em LOW ao parar
    if (pathExists(gpioPath))
    {
        try { writeFile(gpioPath + "/value", "0"); } catch (...) {}
    }
}

void Pin::softPwmWorker()
{
    while (runSoftPwm)
    {
        float freq  = currentFrequency.load();
        float duty  = currentDuty.load();

        // Período em microssegundos
        int periodUs  = static_cast<int>(1e6f / freq);
        int onTimeUs  = static_cast<int>(periodUs * duty);
        int offTimeUs = periodUs - onTimeUs;

        if (onTimeUs > 0)
        {
            // Mutex não é usado aqui para não bloquear a thread de tempo real;
            // a escrita é atômica a nível de sysfs
            writeFile(gpioPath + "/value", "1");
            std::this_thread::sleep_for(std::chrono::microseconds(onTimeUs));
        }

        if (offTimeUs > 0)
        {
            writeFile(gpioPath + "/value", "0");
            std::this_thread::sleep_for(std::chrono::microseconds(offTimeUs));
        }
    }
}

// ========================================================================== //
//  Getters                                                                   //
// ========================================================================== //

float   Pin::getDuty()      const { return currentDuty.load();      }
float   Pin::getFrequency() const { return currentFrequency.load(); }
PinMode Pin::getMode()      const { return mode;                    }
int     Pin::getPinNumber() const { return pinNumber;               }
bool    Pin::isActive()     const { return active;                  }

