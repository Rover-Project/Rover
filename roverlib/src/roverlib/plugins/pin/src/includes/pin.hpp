#ifndef PIN_HPP
#define PIN_HPP

#include <string>
#include <thread>
#include <atomic> // Necessário para evitar conflitos entre threads

enum PinMode { DIGITAL_IN, DIGITAL_OUT, PWM };

class Pin {
private:
    int pinNumber;
    int kernelPin;
    int pwmChannel;
    PinMode mode;
    bool active;

    std::string gpioPath;
    std::string pwmPath;

    // --- NOVOS MEMBROS PARA SOFT-PWM ---
    std::thread softPwmThread;
    std::atomic<bool> runSoftPwm{false};
    std::atomic<float> currentDuty{0.0f};
    void softPwmWorker(); // Função que a thread executará
    // ----------------------------------

    bool pathExists(const std::string& path);
    void validatePin(int pin);
    bool isPWMPin(int pin);
    int gpioToPWMChannel(int pin);
    void writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);

public:
    Pin(int pin, PinMode mode);
    ~Pin();
    void release();
    void write(int value);
    int read();
    void pwmWrite(float duty);
};

#endif