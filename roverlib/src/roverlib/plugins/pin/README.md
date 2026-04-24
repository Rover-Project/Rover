# Pin

Plugin de controle GPIO de baixo nível para a **roverlib**.  
Substitui a dependência do `RPi.GPIO` com uma camada nativa em C++ exposta ao Python via **pybind11**.

---

## Estrutura

```
pin/
├── src/
│   ├── includes/
│   │   └── pin.hpp         # Interface pública da
│   ├── src/                # classe Pin
│   │   └── pin.cpp         # Implementação C++
│   ├── binds.cpp           # Bindings pybind11
│   └── CMakeLists.txt      # Configuração de build
│
├── bin/
│   └── pin.so              # Módulo compilado  
│                           # (gerado pelo CMake)
├── pin.py                  # Abstração Python 
└── README.md               # (interface principal)
```

---

## Dependências

| Ferramenta | Versão mínima | Instalação |
|---|---|---|
| CMake | 3.15 | `sudo apt install cmake` |
| GCC / Clang | C++17 | `sudo apt install build-essential` |
| Python | 3.8+ | — |
| pybind11 | 2.10+ | `pip install pybind11` |

---

## Compilação

```bash
# A partir da raiz do repositório, dentro de pin/src/
cd pin/src
mkdir build && cd build
cmake ..
make -j$(nproc)
```

O arquivo `pin.so` será gerado automaticamente em `pin/bin/`.

---

## Uso

### Importação

```python
from pin.pin import Pin, PinMode
```

### Saída digital

```python
led = Pin(17, PinMode.DIGITAL_OUT)
led.on()          # HIGH
led.off()         # LOW
led.write(1)      # equivalente a on()
led.release()
```

### Entrada digital

```python
botao = Pin(4, PinMode.DIGITAL_IN)
estado = botao.read()   # 0 ou 1
botao.release()
```

### PWM por hardware (pinos 12, 13, 18, 19)

Usa o subsistema `pwmchip0` do kernel — resolução nanosegundo, sem overhead de CPU.

```python
servo = Pin(18, PinMode.PWM)

# Posicionamento de servo (50 Hz, período = 20 ms)
servo.pwm(0.050)    # ~1,0 ms → posição mínima
servo.pwm(0.075)    # ~1,5 ms → posição central
servo.pwm(0.100)    # ~2,0 ms → posição máxima

# Mudar frequência em tempo real
servo.pwm(0.5, frequency=1000)   # 50 % duty, 1 kHz

servo.stop_pwm()    # para sem liberar o pino
servo.release()
```

### PWM por software (qualquer pino DIGITAL_OUT)

Usa uma thread dedicada. Adequado para LEDs, ESCs simples e motores DC quando os pinos de hardware não estão disponíveis. Precisão menor que o hardware PWM.

```python
motor = Pin(17, PinMode.DIGITAL_OUT)
motor.pwm(0.5, frequency=50)    # 50 % duty, 50 Hz

# Alterar parâmetros em tempo real sem reiniciar a thread
motor.pwm(0.75, frequency=50)

motor.stop_pwm()
motor.release()
```

### Context manager (`with`)

O `with` garante que `release()` seja chamado mesmo em caso de exceção:

```python
with Pin(18, PinMode.PWM) as servo:
    servo.pwm(0.075)
    # ... ao sair do bloco, release() é chamado automaticamente
```

---

## Propriedades

```python
pin = Pin(18, PinMode.PWM)

pin.number      # int  → número BCM do pino
pin.mode        # PinMode → modo configurado
pin.active      # bool → True se inicializado e não liberado
pin.duty        # float → duty cycle atual (0.0–1.0)
pin.frequency   # float → frequência PWM atual em Hz
```

---

## Pinos PWM de hardware

| GPIO (BCM) | Canal PWM |
|---|---|
| 12 | PWM0 |
| 18 | PWM0 |
| 13 | PWM1 |
| 19 | PWM1 |

> **Atenção:** os pinos 12/18 compartilham o mesmo canal (PWM0), assim como 13/19 compartilham PWM1. Não é possível configurá-los com parâmetros diferentes simultaneamente.

---

## Offset do kernel

O mapeamento BCM → número do kernel usa o offset **571** (padrão Raspberry Pi 5).  
Para Raspberry Pi 4, altere a constante em `bcmToKernel()` em `pin.cpp`:

```cpp
// RPi 4:
return bcm + 512;

// RPi 5:
return bcm + 571;
```

---

## Permissões

O acesso ao sysfs GPIO requer permissões adequadas. Opções:

```bash
# Opção 1: rodar com sudo (desenvolvimento)
sudo python main.py

# Opção 2: adicionar o usuário ao grupo gpio (produção)
sudo usermod -aG gpio $USER
# (requer logout/login)
```

---
