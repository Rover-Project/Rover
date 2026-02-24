#ifndef PIN_HPP
#define PIN_HPP

#include <string>

enum PinMode {
    INPUT,
    OUTPUT
};

class Pin {
private:
    int pinNumber;
    PinMode mode;

    std::string gpioPath;

    void writeFile(const std::string& path, const std::string& value);
    std::string readFile(const std::string& path);

public:
    Pin(int pin, PinMode mode);
    ~Pin();

    void write(int value);
    int read();
};

#endif
