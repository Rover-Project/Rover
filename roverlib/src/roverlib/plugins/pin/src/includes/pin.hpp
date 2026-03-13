#ifndef PIN_HPP
#define PIN_HPP

#include <string>

enum PinMode
{
    DIGITAL_IN,
    DIGITAL_OUT,
    PWM
};

class Pin
{
private:

    int pinNumber;
    int kernelPin;
    int pwmChannel;

    PinMode mode;
    bool active;
    std::string gpioPath;
    std::string pwmPath;

    int pwmPeriod = 20000000;

    void writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);

    int bcmToKernel(int bcm);
    int gpioToPwmChannel(int gpio);

public:

    Pin(int pin, PinMode mode);

    void write(int value);
    int read();

    void pwmWrite(int dutyPercent);

    void release();

    ~Pin();
};

#endif