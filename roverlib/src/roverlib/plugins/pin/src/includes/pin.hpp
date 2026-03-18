#ifndef PIN_HPP
#define PIN_HPP

#include <string>

enum PinMode {
    DIGITAL_IN,
    DIGITAL_OUT,
    PWM
};

class Pin {
private:
    int pinNumber;
    int kernelPin;
    int pwmChannel;
    PinMode mode;
    bool active;
    std::string gpioPath;
    std::string pwmPath;

    bool pathExists(const std::string& path);
    void validatePin(int pin);
    bool isPWMPin(int pin);
    int gpioToPWMChannel(int pin);
    void writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);
    void setupHardwareMux(int pin, PinMode mode); // Nova: Configura o RP1

public:
    Pin(int pin, PinMode mode);
    ~Pin();
    void release();
    void write(int value);
    int read();
    void pwmWrite(float duty);
};

#endif