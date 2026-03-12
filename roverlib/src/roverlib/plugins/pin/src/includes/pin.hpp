#ifndef PIN_HPP
#define PIN_HPP

#include <string>

enum PinMode
{
    DIGITAL_IN = 0,
    DIGITAL_OUT = 1,
    PWM = 2
};

class Pin
{
private:

    int pinNumber;
    int kernelPin;
    int pwmChannel;

    PinMode mode;

    std::string gpioPath;
    std::string pwmPath;

    bool active;

    void validatePin(int pin);
    bool isPWMPin(int pin);

    void writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);
    bool pathExists(const std::string& path);

public:

    Pin(int pin, PinMode mode);
    ~Pin();

    void write(int value);
    int read();

    void pwmWrite(float duty);

    void release();
};

#endif
