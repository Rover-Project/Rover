#include "../include/pin.hpp"

extern "C" {

    Pin* pin_create(int pin, int mode) {
        return new Pin(pin, (PinMode)mode);
    }

    void pin_write(Pin* p, int value) {
        if (p) p->write(value);
    }

    int pin_read(Pin* p) {
        if (p) return p->read();
        return -1;
    }

    void pin_destroy(Pin* p) {
        delete p;
    }
}
