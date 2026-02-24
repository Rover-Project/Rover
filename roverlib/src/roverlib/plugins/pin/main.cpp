#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

// ================= ENUM =================
enum PinMode {
    INPUT,
    OUTPUT
};

// ================= CLASSE =================
class Pin {
private:
    int pinNumber;
    PinMode mode;
    std::string gpioPath;

    void writeFile(const std::string& path, const std::string& value) {
        std::ofstream file(path);
        if (!file) {
            std::cerr << "Erro ao abrir " << path << "\n";
            return;
        }
        file << value;
    }

    std::string readFile(const std::string& path) {
        std::ifstream file(path);
        std::string value;
        file >> value;
        return value;
    }

public:
    Pin(int pin, PinMode mode) {
        this->pinNumber = pin;
        this->mode = mode;

        gpioPath = "/sys/class/gpio/gpio" + std::to_string(pinNumber);

        // exporta pino
        writeFile("/sys/class/gpio/export", std::to_string(pinNumber));

        // espera o sistema criar o diretório
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // define direção
        if (mode == OUTPUT) {
            writeFile(gpioPath + "/direction", "out");
        } else {
            writeFile(gpioPath + "/direction", "in");
        }
    }

    ~Pin() {
        writeFile("/sys/class/gpio/unexport", std::to_string(pinNumber));
    }

    void write(int value) {
        if (mode != OUTPUT) {
            std::cerr << "Erro: pino não é OUTPUT\n";
            return;
        }
        writeFile(gpioPath + "/value", std::to_string(value));
    }

    int read() {
        std::string val = readFile(gpioPath + "/value");
        try {
            return std::stoi(val);
        } catch (...) {
            return -1;
        }
    }
};

// ================= MAIN =================
int main() {
    // GPIO 15 = pino físico 10
    Pin led(15, OUTPUT);

    while (true) {
        std::cout << "LED ON\n";
        led.write(1);
        std::this_thread::sleep_for(std::chrono::seconds(1));

        std::cout << "LED OFF\n";
        led.write(0);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    return 0;
}
