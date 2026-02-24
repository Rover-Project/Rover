#include "pin.hpp"
#include <thread>
#include <chrono>

int main() {
    Pin led(15, OUTPUT);

    while (true) {
        led.write(1);
        std::this_thread::sleep_for(std::chrono::seconds(1));

        led.write(0);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}