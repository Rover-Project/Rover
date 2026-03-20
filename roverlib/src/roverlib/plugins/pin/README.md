# PIN Plugin

Módulo responsável pelo controle de **GPIO e PWM** da Raspberry Pi utilizando uma implementação híbrida **C++ + Python**.

A biblioteca fornece uma API simples em Python para manipulação de pinos digitais e PWM, enquanto a implementação de baixo nível é feita em C++ para garantir maior desempenho e controle direto sobre o sistema.

---

# Arquitetura do Módulo

O módulo segue uma arquitetura em camadas:

```
Python Application
        │
        ▼
      pin.py
(API de alto nível em Python)
        │
        ▼
      pin.so
(Biblioteca nativa compilada)
        │
        ▼
      C++
(Acesso direto ao sistema Linux)
```

A camada Python fornece uma interface amigável para o usuário, enquanto a camada C++ realiza o acesso direto aos arquivos de controle do kernel Linux.

O módulo é compilado utilizando **CMake** e integrado ao Python através da biblioteca pybind11.

---

# Estrutura do Diretório

```
pin
│
├── src
│   ├── includes
│   │   └── pin.hpp
│   │
│   ├── src
│   │   └── pin.cpp
│   │
│   ├── binds.cpp
│   └── CMakeLists.txt
│
├── bin
│   └── pin.so
│
├── pin.py
│
├── testLedApi.py
├── testPwm.py
│
└── README.md
```

Descrição dos componentes:

| Arquivo          | Descrição                                      |
| ---------------- | ---------------------------------------------- |
| `pin.hpp`        | Definição da classe Pin                        |
| `pin.cpp`        | Implementação da lógica de controle GPIO e PWM |
| `binds.cpp`      | Interface entre C++ e Python                   |
| `CMakeLists.txt` | Configuração de compilação                     |
| `pin.so`         | Biblioteca compilada utilizada pelo Python     |
| `pin.py`         | Classe de abstração Python                     |
| `testLedApi.py`  | Teste de controle digital                      |
| `testPwm.py`     | Teste de controle PWM                          |

---

# Funcionalidades

O módulo permite:

* Criar um pino GPIO
* Configurar modo do pino
* Ler valores digitais
* Escrever valores digitais
* Gerar sinal PWM
* Liberar o pino após uso
* Validar erros de uso incorreto

---

# Modos de Operação

Os modos disponíveis são:

```
PinMode.DIGITAL_IN
PinMode.DIGITAL_OUT
PinMode.PWM
```

| Modo        | Descrição                |
| ----------- | ------------------------ |
| DIGITAL_IN  | leitura de sinal digital |
| DIGITAL_OUT | escrita de sinal digital |
| PWM         | geração de sinal PWM     |

---

# GPIO suportados

Os GPIO válidos são:

```
0 - 27
```

Para PWM apenas os pinos abaixo são suportados:

```
12
13
18
19
```

Caso um pino inválido seja utilizado, o sistema lança uma exceção.

---

# Compilação

A biblioteca precisa ser compilada antes de ser utilizada.

Entre no diretório do plugin:

```
cd roverlib/plugins/pin
```

Crie o diretório de build:

```
mkdir build
cd build
```

Configure o projeto:

```
cmake ../src
```

Compile a biblioteca:

```
make
```

Após a compilação o arquivo `.so` deve ser copiado para o diretório `bin`.

---

# Uso em Python

Exemplo de controle digital:

```python
from pin import Pin, PinMode
import time

led = Pin(17, PinMode.DIGITAL_OUT)

try:

    while True:

        led.on()
        time.sleep(1)

        led.off()
        time.sleep(1)

finally:

    led.release()
```

---

# Exemplo PWM

```python
from pin import Pin, PinMode
import time

led = Pin(18, PinMode.PWM)

try:

    led.pwm(0.1)
    time.sleep(2)

    led.pwm(0.5)
    time.sleep(2)

    led.pwm(0.9)
    time.sleep(2)

finally:

    led.release()
```

O valor de PWM deve estar entre:

```
0.0 → 0%
1.0 → 100%
```

---

# Tratamento de Erros

O módulo implementa diversas validações para evitar uso incorreto:

| Erro                   | Descrição                                  |
| ---------------------- | ------------------------------------------ |
| GPIO inválido          | pino fora do intervalo permitido           |
| PWM em pino não PWM    | tentativa de usar PWM em pino incompatível |
| Escrita em pino INPUT  | tentativa de escrita em pino de entrada    |
| Leitura em pino OUTPUT | tentativa de leitura em pino de saída      |
| Duty cycle inválido    | valor de PWM fora do intervalo permitido   |

Essas validações geram exceções que podem ser tratadas pelo Python.

---

# Liberação de Recursos

Sempre que um pino não estiver mais em uso ele deve ser liberado:

```python
pin.release()
```

Isso remove o pino do controle do kernel Linux e evita conflitos com outros módulos.

---

# Sistema Operacional

O módulo foi desenvolvido para execução em:

* Raspberry Pi OS
* Linux

utilizando a interface do kernel:

```
/sys/class/gpio
/sys/class/pwm
```

---

# Dependências

Para compilar o módulo são necessárias as seguintes ferramentas:

```
CMake
g++
pybind11
Python3
```

---

# Objetivo do Módulo

Este plugin foi desenvolvido para servir como **base de controle de hardware** para o projeto Rover.

Outros módulos poderão utilizar este plugin para controlar:

* motores
* servos
* sensores digitais
* encoders
* atuadores PWM

Centralizando toda a manipulação de GPIO em uma única biblioteca.


(ARQUIVO DE TESTE: PASSIVO DE MUDANÇAS FUTURAS)