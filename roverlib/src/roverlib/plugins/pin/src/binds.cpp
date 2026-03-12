#include <pybind11/pybind11.h>
#include "includes/pin.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pin, m)
{
    py::enum_<PinMode>(m, "PinMode")
        .value("DIGITAL_IN", DIGITAL_IN)
        .value("DIGITAL_OUT", DIGITAL_OUT)
        .value("PWM", PWM);

    py::class_<Pin>(m, "Pin")
        .def(py::init<int, PinMode>())
        .def("write", &Pin::write)
        .def("read", &Pin::read)
        .def("pwmWrite", &Pin::pwmWrite)
        .def("release", &Pin::release);
}
