#include <pybind11/pybind11.h>
#include "includes/pin.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_pin_native, m)
{
m.doc() = "Módulo nativo de controle GPIO para Raspberry Pi (roverlib).";

// ---------------------------------------------------------------------- //
//  Enum PinMode                                                           //
// ---------------------------------------------------------------------- //
py::enum_<PinMode>(m, "PinMode",
"Modos de operação de um pino GPIO.")
.value("DIGITAL_IN",  DIGITAL_IN,  "Entrada digital.")
.value("DIGITAL_OUT", DIGITAL_OUT, "Saída digital.")
.value("PWM",         PWM,         "Saída PWM (hardware nos pinos 12/13/18/19).")
.export_values();

// ---------------------------------------------------------------------- //
//  Classe Pin                                                             //
// ---------------------------------------------------------------------- //
py::class_<Pin>(m, "Pin",
R"doc(
Controla um pino GPIO da Raspberry Pi.

Parâmetros
----------
pin : int
Número BCM do pino (0–27).
mode : PinMode
Modo de operação: DIGITAL_IN, DIGITAL_OUT ou PWM.

Exemplos
--------
>>> from pin import pin as native
>>> led = native.Pin(17, native.PinMode.DIGITAL_OUT)
>>> led.write(1)
>>> led.release()
)doc")

// Construtor
.def(py::init<int, PinMode>(),
        py::arg("pin"), py::arg("mode"))

// Interface digital
.def("write", &Pin::write,
        py::arg("value"),
        "Escreve 0 ou 1 em um pino DIGITAL_OUT.")

.def("read", &Pin::read,
        "Lê o valor (0 ou 1) de um pino DIGITAL_IN.")

// Interface PWM
.def("pwmWrite", &Pin::pwmWrite,
        py::arg("duty"), py::arg("frequency_hz") = 50.0f,
        R"doc(
        Configura e inicia o sinal PWM.

        Parâmetros
        ----------
        duty : float
        Ciclo de trabalho entre 0.0 (0 %) e 1.0 (100 %).
        frequency_hz : float, opcional
        Frequência em Hz (padrão: 50 Hz).
        )doc")

.def("pwmStop", &Pin::pwmStop,
        "Para o sinal PWM sem liberar o pino.")

// Liberação
.def("release", &Pin::release,
        "Libera o pino do sysfs e encerra threads ativas.")

// Getters informativos
.def("getDuty",      &Pin::getDuty,
        "Retorna o duty cycle atual (0.0–1.0).")

.def("getFrequency", &Pin::getFrequency,
        "Retorna a frequência PWM atual em Hz.")

.def("getMode",      &Pin::getMode,
        "Retorna o PinMode configurado.")

.def("getPinNumber", &Pin::getPinNumber,
        "Retorna o número BCM do pino.")

.def("isActive",     &Pin::isActive,
        "Retorna True se o pino está inicializado e ativo.")

// Representação textual conveniente no REPL
.def("__repr__", [](const Pin& p) {
std::string modeStr;
switch (p.getMode()) {
        case DIGITAL_IN:  modeStr = "DIGITAL_IN";  break;
        case DIGITAL_OUT: modeStr = "DIGITAL_OUT"; break;
        case PWM:         modeStr = "PWM";         break;
}
return "<Pin bcm=" + std::to_string(p.getPinNumber()) +
        " mode="    + modeStr +
        " active="  + (p.isActive() ? "True" : "False") + ">";
});
}