# Motor

Driver de baixo nível para controle de motores DC via Ponte-H L298N, com suporte a modo virtual para simulação e testes sem hardware.

---

## Sumário
 
- [Visão Geral](#visão-geral)
- [Estrutura do Plugin](#estrutura-do-plugin)
- [Instalação e Requisitos](#instalação-e-requisitos)
- [Uso Rápido](#uso-rápido)
- [Referência da API](#referência-da-api)
  - [MotorInterface](#motorinterface)
  - [MotorDriver](#motordriver)
  - [VirtualMotor](#virtualmotor)
  - [Exceções](#exceções)
- [Diagrama de Classes](#diagrama-de-classes)
- [Direções de Rotação](#direções-de-rotação)
- [Exemplos](#exemplos)
---

## Visão Geral

O plugin motor fornece uma abstração para controle de motores DC conectados a uma **Ponte-H L298N** em uma Raspberry Pi. Ele é composto por:

| Classe | Descrição |
|---|---|
| `MotorInterface` | Contrato abstrato (ABC) que define o comportamento esperado de qualquer driver de motor |
| `MotorDriver` | Implementação real que usa o plugin `pin` (C++/pybind11) para controlar os pinos GPIO |
| `VirtualMotor` | Implementação de simulação — permite desenvolver e testar lógica sem hardware físico |

---

## Estrutura do Plugin

```
motor/
├── __init__.py
├── motorInterface.py   # Classe base abstrata
├── motorDriver.py      # Driver real (requer Raspberry Pi + plugin pin)
├── virtualMotor.py     # Driver de simulação
└── exceptions.py       # Exceções customizadas
```

---

## Instalação e Requisitos

### Modo Virtual (simulação)

Não exige dependências externas. Funciona em qualquer sistema com Python 3.10+.

```python
from roverlib.plugins.motor.virtualMotor import VirtualMotor
```

### Modo Real (Raspberry Pi)

Requer:
- Raspberry Pi com GPIO disponível
- Plugin `pin` compilado (`roverlib.plugins.pin`)

```python
from roverlib.plugins.motor.motorDriver import MotorDriver
```

> ⚠️ Se o plugin `pin` não estiver disponível, a importação de `MotorDriver` levantará `ImportError` com uma mensagem explicativa.

---

## Uso Rápido

```python
from roverlib.plugins.motor.virtualMotor import VirtualMotor

# Instancia o motor com os pinos GPIO e uma tag identificadora
motor = VirtualMotor(pins=(17, 18), tag="motor_esquerdo")

# Inicializa os recursos
motor.initialize()

# Move para frente a 75% de velocidade
motor.set_movement(speed=75, direction="FORWARD")

# Move para trás a 50%
motor.set_movement(speed=50, direction="BACKWARD")

# Para o motor
motor.stop()

# Libera os recursos ao fim do uso
motor.cleanup()
```

---

## Referência da API

### `MotorInterface`

> `motorInterface.py`

Classe base abstrata (ABC). Define o contrato que todo driver de motor deve seguir.

Todos os métodos abaixo são abstratos e devem ser implementados pelas subclasses.

---

#### `__init__(pins, pwm_frequency=1000)`

| Parâmetro       | Tipo              | Descrição                                              |
|-----------------|-------------------|--------------------------------------------------------|
| `pins`          | `tuple[int, int]` | Pinos GPIO conectados às entradas IN1 e IN2 da Ponte-H |
| `pwm_frequency` | `int`             | Frequência do sinal PWM em Hz (padrão: `1000`)         |

---

#### `initialize()`

Configura os pinos GPIO e inicia os sinais PWM. Deve ser chamado antes de qualquer operação de movimento.

---

#### `set_movement(speed, direction="FORWARD")`

Controla a velocidade e direção de rotação do motor.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `speed` | `float` | Velocidade de rotação de `0.0` a `100.0` (%) |
| `direction` | `str` | Direção: `"FORWARD"`, `"BACKWARD"` ou `"STOP"` |

**Exceções:**
- `UninitializedMotorError` — motor não foi inicializado.
- `DirectionInvalidMotorError` — direção de rotação inválida.

---

#### `stop()`

Para imediatamente a rotação do motor (atalho para `set_movement(0, "STOP")`).

---

#### `cleanup()`

Para o motor e libera os recursos GPIO alocados.

---

### `MotorDriver`

> `motorDriver.py`

Implementação real do `MotorInterface` utilizando o plugin `pin` (C++/pybind11).

**Parâmetros adicionais no `__init__`:**

Mesmos parâmetros da interface. Lança `ImportError` se o plugin `pin` não estiver disponível.

**Atributos internos:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `_pin1` | `Pin \| None` | Objeto Pin para IN1 |
| `_pin2` | `Pin \| None` | Objeto Pin para IN2 |
| `_initialized` | `bool` | Flag de estado de inicialização |

**Comportamento de `cleanup()`:**  
Além de parar o motor, chama `release()` em ambos os pinos e os define como `None`.

---

### `VirtualMotor`

> `virtualMotor.py`

Implementação de simulação do `MotorInterface`. Não interage com hardware real — apenas imprime as ações no terminal. Ideal para testes e desenvolvimento.

**Parâmetros adicionais no `__init__`:**

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `tag` | `str` | Nome/identificador do motor (usado nos logs) |

**Exemplo de saída no terminal:**

```
MotorDriver motor_esquerdo inicializado. Frequência PWM: 1000Hz
motor_esquerdo: Frente - velocidade: 75.0
motor_esquerdo: Trás - velocidade: 50.0
motor_esquerdo: Parado - velocidade: 0
MotorDriver motor_esquerdo: recursos liberados.
```

---

### Exceções

> `exceptions.py`

| Exceção | Herda de | Quando é levantada |
|---|---|---|
| `UninitializedMotorError` | `Exception` | Ao chamar `set_movement()` ou `stop()` antes de `initialize()` |
| `DirectionInvalidMotorError` | `Exception` | Ao passar uma direção inválida para `set_movement()` |
| `MotorCreationError` | `Exception` | Falha na criação do motor (e.g. GPIO indisponível) |

---

## Diagrama de Classes

```
MotorInterface (ABC)
│
├── MotorDriver          ← Raspberry Pi (plugin pin)
│
└── VirtualMotor         ← Simulação / Testes
```

---

## Direções de Rotação

| Valor | Efeito |
|---|---|
| `"FORWARD"` | Rotação para frente |
| `"BACKWARD"` | Rotação para trás |
| `"STOP"` | Para o motor (duty cycle 0 em ambos os pinos) |

> A comparação de direção é **case-insensitive**: `"forward"`, `"Forward"` e `"FORWARD"` são equivalentes.

A velocidade é sempre **normalizada** para o intervalo `[0.0, 100.0]`, utilizando `min(abs(speed), 100.0)`.

---

## Exemplos

### Usando `MotorDriver`

```python
from roverlib.plugins.motor.motorDriver import MotorDriver

motor = MotorDriver(pins=(17, 18), pwm_frequency=1000)
motor.initialize()

motor.set_movement(speed=60, direction="FORWARD")

motor.cleanup()
```

### Tratamento de Exceções

```python
from roverlib.plugins.motor.virtualMotor import VirtualMotor
from roverlib.plugins.motor.exceptions import UninitializedMotorError, DirectionInvalidMotorError

motor = VirtualMotor(pins=(17, 18), tag="motor_teste")

try:
    motor.set_movement(50)  # Erro: não inicializado
except UninitializedMotorError as e:
    print(f"Erro: {e}")

motor.initialize()

try:
    motor.set_movement(50, direction="ESQUERDA")  # Erro: direção inválida
except DirectionInvalidMotorError as e:
    print(f"Erro: {e}")
```

### Dois motores em paralelo

```python
from roverlib.plugins.motor.virtualMotor import VirtualMotor

left  = VirtualMotor(pins=(17, 18), tag="esquerdo")
right = VirtualMotor(pins=(22, 23), tag="direito")

for motor in (left, right):
    motor.initialize()

# Avançar
left.set_movement(80, "FORWARD")
right.set_movement(80, "FORWARD")

# Curva à direita (reduz motor direito)
left.set_movement(80, "FORWARD")
right.set_movement(30, "FORWARD")

# Parar
left.stop()
right.stop()

for motor in (left, right):
    motor.cleanup()
```
