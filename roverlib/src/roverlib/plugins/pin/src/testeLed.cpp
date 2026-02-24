#include "pin.hpp"
#include <unistd.h>

int main() {
    Pin led(17, OUTPUT);

    while (true) {
        led.write(1);
        sleep(1);
        led.write(0);
        sleep(1);
    }
}
