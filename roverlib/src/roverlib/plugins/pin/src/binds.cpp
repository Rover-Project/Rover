#include <pybind11/pybind11.h>
#include "include/pin.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pin, m)
{

    py::enum_<PinMode>(m, "PinMode")
        .value("INPUT", INPUT)
        .value("OUTPUT", OUTPUT);

    py::class_<Pin>(m, "Pin")

        .def(py::init<int, PinMode>())

        .def("write", &Pin::write)

        .def("read", &Pin::read);
}
