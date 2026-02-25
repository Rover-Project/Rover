#include "../include/pin.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    Pin led(15, OUTPUT);

    bool running = true;

    std::thread inputThread([&running]() {
        char c;
        while (std::cin >> c) {
            if (c == 'q') {
                running = false;
                break;
            }
        }
    });

    while (running) {
        std::cout << "LED ON\n";
        led.write(1);
        std::this_thread::sleep_for(std::chrono::seconds(1));

        std::cout << "LED OFF\n";
        led.write(0);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    std::cout << "Encerrando e liberando GPIO...\n";

    inputThread.join();  // <-- CORRETO
    return 0;
}