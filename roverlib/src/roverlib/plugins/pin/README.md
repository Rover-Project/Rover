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
│   └── CMakeLists.txt      # Build manual (CMake), opcional
│
├── _pin_native*.so         # Módulo compilado pelo `pip install` (não versionado)
├── bin/                    # Módulo compilado à mão com CMake (reserva)
├── pin.py                  # Abstração Python (interface principal)
├── __init__.py             # API pública
├── exceptions.py           # PinNotAvailable
├── examples/               # scripts de demonstração (exigem a Raspberry Pi)
├── tests/                  # testes (PC + hardware)
└── README.md
```

---

## Compilação

### Automática (normal)

O módulo nativo é compilado pelo próprio `pip install` da RoverLib (ver `roverlib/setup.py`), **na Raspberry Pi e para a versão de Python em uso**. Não há passo manual: o `rover_setup.sh` já instala o necessário.

| Requisito | Instalação |
|---|---|
| Compilador C++17 | `sudo apt install build-essential` |
| Cabeçalhos do Python | `sudo apt install python3-dev` |
| pybind11 | instalado sozinho pelo `pip` durante o build |

- **No PC** (Windows, macOS, Linux x86) a extensão não é compilada e a RoverLib funciona em modo simulação.
- **A extensão é opcional:** se a compilação falhar, a instalação termina mesmo assim; ao importar o plugin na Raspberry Pi aparece um aviso com o motivo e os comandos para resolver.
- Para recompilar (por exemplo, depois de trocar de versão do Python):

```bash
pip install -e roverlib --no-deps --force-reinstall -v
```

Variáveis de ambiente do build: `ROVER_BUILD_NATIVE=1` compila em qualquer Linux (útil para testar a compilação no PC); `ROVER_BUILD_NATIVE=0` nunca compila.

### Endereço dos pinos (offset da GPIO)

No sysfs, o pino BCM *n* é o número *base + n*, e a base muda com o modelo e o kernel (Pi 5: 571; Pi 4: 512). O módulo descobre a base lendo `/sys/class/gpio/gpiochip*/label` (`pinctrl-rp1`, `pinctrl-bcm2711` ou `pinctrl-bcm2835`). Para conferir: `python -c "from roverlib.plugins.pin import gpio_base; print(gpio_base())"`. Se a detecção falhar, force o valor com a variável `ROVER_GPIO_BASE`.

### Manual com CMake (opcional)

```bash
cd roverlib/src/roverlib/plugins/pin/src
mkdir build && cd build
cmake ..
make -j$(nproc)
```

O módulo é gerado em `pin/bin/`, usado quando não há um módulo compilado pelo `pip`.

---

## Uso

### Importação

```python
from roverlib.plugins.pin import Pin, PinMode
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

---

## Simulação

O plugin `pin` não tem versão simulada: ele é a base dos drivers de GPIO. Sem o módulo nativo (PC, ou Raspberry Pi em que a compilação falhou), o plugin continua importável, `HARDWARE_AVAILABLE` vale `False` e criar um `Pin` gera `PinNotAvailable` (um `RuntimeError`). Quem simula são os plugins acima dele, como o `VirtualMotor`.

---

## Testes

```bash
python -m pytest src/roverlib/plugins/pin                                     # PC: módulo nativo falso
ROVER_TEST_PIN=21 python -m pytest -m hardware src/roverlib/plugins/pin      # Raspberry Pi
```

Os testes de hardware só rodam com `ROVER_TEST_PIN` definido: use um pino **livre**, sem nada ligado (os pinos dos motores, como o 17, moveriam as rodas).

Scripts de demonstração em `examples/` (na Raspberry Pi): `demo_digital.py`, `demo_hw_pwm.py`, `demo_soft_pwm.py` e `interactive.py`.
