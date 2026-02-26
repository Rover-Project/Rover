#include <pybind11/pybind11.h>
#include "../include/pin.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pin, m) {
    m.doc() = "GPIO control module using sysfs";

    py::enum_<PinMode>(m, "PinMode")
        .value("INPUT", INPUT)
        .value("OUTPUT", OUTPUT)
        .export_values();

    py::class_<Pin>(m, "Pin")
        .def(py::init<int, PinMode>())
        .def("write", &Pin::write)
        .def("read", &Pin::read);
}

