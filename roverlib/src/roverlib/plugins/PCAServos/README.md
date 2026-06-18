# Módulo PCA9685

Biblioteca própria para controle do chip **PCA9685** via comunicação I2C direta, desenvolvida para controle de servomotores embarcados em um robô móvel (rover) baseado em Raspberry Pi 5.

Esta biblioteca **não depende da `adafruit_pca9685`** — toda a comunicação com o chip é feita diretamente via `smbus2`, implementando do zero a lógica de registradores, cálculo de frequência e geração de PWM descrita no datasheet oficial do componente.

---

## Sumário

- [Objetivo do módulo](#objetivo-do-módulo)
- [Como o PCA9685 funciona](#como-o-pca9685-funciona)
- [Estrutura de arquivos e pastas](#estrutura-de-arquivos-e-pastas)
- [Instalação](#instalação)
- [Guia rápido de uso](#guia-rápido-de-uso)
- [Referência de classes e funções](#referência-de-classes-e-funções)
  - [PCA9685Driver](#pca9685driver)
  - [PCAServos](#pcaservos)
  - [Servo](#servo)
  - [ContinuousServo](#continuousservo)
- [Exceções](#exceções)
- [Testes](#testes)
- [Conexões físicas (hardware)](#conexões-físicas-hardware)
- [Notas e boas práticas](#notas-e-boas-práticas)

---

## Objetivo do módulo

O PCA9685 é um chip controlador de PWM com 16 canais independentes, muito usado para controlar servomotores e LEDs. Este módulo foi criado para:

1. Eliminar a dependência da biblioteca `adafruit_pca9685`, mantendo a mesma facilidade de uso
2. Expor uma interface simples e direta (`PCAServos`, `Servo`, `ContinuousServo`) para controlar servos de câmera (pan/tilt) e outros atuadores do rover
3. Servir como material de estudo sobre comunicação I2C e geração de PWM em baixo nível
4. Ser modular o suficiente para ser reaproveitado em outros projetos que usem o PCA9685, não apenas no rover

---

## Como o PCA9685 funciona

O chip possui um **oscilador interno de 25 MHz**. Esse clock é dividido por um valor chamado `prescale`, que define a frequência final do PWM (normalmente 50 Hz para servos). A partir disso, um contador interno de 12 bits (0 a 4095) repete um ciclo continuamente nessa frequência.

Cada um dos 16 canais tem dois registradores de 12 bits:

- **ON**: o instante (tick, de 0 a 4095) em que a saída do canal sobe para HIGH
- **OFF**: o instante em que a saída cai para LOW

A diferença entre `OFF` e `ON`, dividida por 4096, define o **duty cycle** — ou seja, a porcentagem do período em que o pino fica em nível alto. Para servomotores, isso se traduz em uma largura de pulso (geralmente entre 0.5 ms e 2.5 ms a 50 Hz), que o servo interpreta como uma posição angular.

```
Frequência (Hz)  →  prescale = round(25_000_000 / (4096 × freq)) − 1
Duty cycle        →  (OFF − ON) / 4096
Largura de pulso  →  duty_cycle × período_total
```

Toda a comunicação com o chip é feita por **I2C**, escrevendo e lendo bytes em registradores específicos (endereços fixos definidos pelo datasheet), usando o endereço padrão `0x40`.

---

## Estrutura de arquivos e pastas

```
PCAServos/
├── pca9685/                  # Pacote principal da biblioteca
│   ├── __init__.py           # Exporta as classes públicas do módulo
│   ├── driver.py             # Comunicação I2C de baixo nível (registradores)
│   └── servos.py             # Interface de alto nível (ângulos, throttle)
│
├── tests/                    # Testes unitários (sem necessidade de hardware)
│   ├── __init__.py
│   ├── mock_smbus2.py        # Simulação do barramento I2C para testes
│   └── test_driver.py        # 39 testes cobrindo driver e classes de servo
│
├── examples/                 # Scripts de exemplo prontos para executar
│   ├── teste_conexao.py      # Teste de fumaça: verifica comunicação I2C
│   └── camera_pantilt.py     # Exemplo de controle de câmera pan/tilt
│
├── setup.py                  # Empacotamento do módulo (pip install -e .)
└── README.md                 # Este documento
```

### Descrição dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `pca9685/driver.py` | Fala diretamente com o chip via I2C. Não sabe o que é um "servo" — só entende registradores, bytes e frequência. |
| `pca9685/servos.py` | Camada de conveniência. Traduz conceitos físicos (graus, velocidade) em chamadas para o driver. |
| `tests/mock_smbus2.py` | Substitui o `smbus2` real por um dicionário em memória, permitindo testar a lógica sem hardware. |
| `tests/test_driver.py` | Valida matematicamente cálculos de frequência, conversão de ângulo, duty cycle, etc. |
| `examples/teste_conexao.py` | Confirma que a Raspberry Pi consegue se comunicar com o PCA9685 físico. |
| `examples/camera_pantilt.py` | Demonstra o uso real com dois servos controlando uma câmera. |

---

## Instalação

Na Raspberry Pi (ou em qualquer máquina Linux com I2C disponível):

```bash
python3 -m venv venv
source venv/bin/activate
pip install smbus2
pip install -e .          # instala o módulo pca9685 em modo editável
```

Para rodar os testes unitários (não precisa de hardware):

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Guia rápido de uso

```python
from pca9685 import PCAServos, Servo, ContinuousServo

# 1. Inicializa o controlador (abre o barramento I2C e configura 50 Hz)
pca = PCAServos(address=0x40, bus=1, frequency=50)

# 2. Controle direto de um canal (estilo "baixo nível")
pca.set_pwm(channel=0, on=0, off=307)        # ~7.5% duty cycle (servo neutro)

# 3. Servo convencional (0°–180°) — câmera, por exemplo
pan = Servo(pca, channel=0)
pan.angle = 90        # centro
pan.angle = 0         # extremo esquerdo
pan.angle = 180        # extremo direito

# 4. Servo de rotação contínua (360°) — ex.: roda do rover
motor = ContinuousServo(pca, channel=1)
motor.throttle = 0.5   # 50% de velocidade, sentido positivo
motor.throttle = -1.0  # velocidade máxima, sentido reverso
motor.stop()             # para o motor

# 5. Encerrar corretamente (libera o barramento I2C)
pca.close()
```

Também é possível usar como *context manager*, garantindo que o barramento seja sempre fechado, mesmo se ocorrer um erro:

```python
with PCAServos() as pca:
    servo = Servo(pca, channel=0)
    servo.angle = 90
```

---

## Referência de classes e funções

### PCA9685Driver

Localização: `pca9685/driver.py`

Driver de baixo nível. Fala diretamente com os registradores do chip via I2C. Normalmente você não precisa instanciar esta classe diretamente — use `PCAServos`, que já a encapsula. Use `PCA9685Driver` apenas se quiser controle total e granular dos registradores.

#### `PCA9685Driver(address=0x40, bus=1, osc_clock=25_000_000)`

Inicializa a comunicação I2C com o chip e o coloca em um estado padrão conhecido.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `address` | `int` | Endereço I2C do PCA9685. Padrão: `0x40`. |
| `bus` | `int` | Número do barramento I2C da Raspberry Pi (geralmente `1`). |
| `osc_clock` | `int` | Frequência do oscilador interno em Hz. Padrão: `25_000_000`. |

---

#### `set_frequency(frequency: float) -> None`

Configura a frequência PWM para **todos** os canais simultaneamente.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `frequency` | `float` | Frequência desejada em Hz. Faixa válida: **24 a 1526 Hz**. Para servos RC convencionais, use `50`. |

**Levanta:** `InvalidFrequencyError` se o valor estiver fora da faixa permitida.

---

#### `get_frequency() -> float \| None`

Retorna a última frequência configurada, ou `None` se `set_frequency` nunca foi chamado.

---

#### `set_pwm(channel: int, on: int, off: int) -> None`

Configura os valores ON e OFF (em ticks de 0 a 4095) de um canal específico.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `channel` | `int` | Canal PWM, de `0` a `15`. |
| `on` | `int` | Tick (0–4095) em que a saída sobe para HIGH. Geralmente `0`. |
| `off` | `int` | Tick (0–4095) em que a saída cai para LOW. Define o duty cycle. |

**Levanta:** `InvalidChannelError` se `channel` estiver fora de 0–15.

---

#### `set_duty_cycle(channel: int, value: int) -> None`

Atalho para `set_pwm(channel, 0, value)`.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `channel` | `int` | Canal PWM (0–15). |
| `value` | `int` | Valor absoluto de duty cycle (0 a 4095). |

---

#### `set_duty_cycle_percent(channel: int, percent: float) -> None`

Define o duty cycle em percentual, mais intuitivo que usar ticks diretamente.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `channel` | `int` | Canal PWM (0–15). |
| `percent` | `float` | Percentual de 0.0 a 100.0 (ex.: `7.5` para o neutro típico de servo). |

---

#### `set_all_pwm(on: int, off: int) -> None`

Define ON e OFF para **todos** os 16 canais ao mesmo tempo, usando os registradores especiais `ALL_LED`.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `on` | `int` | Tick HIGH (0–4095) aplicado a todos os canais. |
| `off` | `int` | Tick LOW (0–4095) aplicado a todos os canais. |

---

#### `get_pwm(channel: int) -> tuple[int, int]`

Lê os valores ON e OFF atuais de um canal direto do chip.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `channel` | `int` | Canal PWM (0–15). |

**Retorna:** tupla `(on, off)`.

---

#### `reset_channel(channel: int) -> None`

Zera um canal específico (ON=0, OFF=0), desativando sua saída.

#### `reset_all_channels() -> None`

Zera todos os 16 canais.

#### `close() -> None`

Zera todos os canais e fecha o barramento I2C. Deve ser sempre chamado ao final do uso (ou use o context manager `with`).

---

### PCAServos

Localização: `pca9685/servos.py`

Interface principal recomendada para uso no projeto. Encapsula o `PCA9685Driver` e adiciona conveniências como controle por microssegundos.

#### `PCAServos(address=0x40, bus=1, frequency=50)`

Inicializa o controlador e já configura a frequência PWM informada.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `address` | `int` | Endereço I2C do PCA9685. Padrão: `0x40`. |
| `bus` | `int` | Barramento I2C da Raspberry Pi. Padrão: `1`. |
| `frequency` | `float` | Frequência PWM em Hz. Padrão: `50` (padrão para servos RC). |

---

#### `set_frequency(frequency: float) -> None`

Reconfigura a frequência PWM (afeta todos os canais). Mesma semântica do driver.

#### `set_pwm(channel: int, on: int, off: int) -> None`

Controle direto de ticks ON/OFF de um canal. Idêntico ao do driver, exposto aqui por conveniência.

#### `set_duty_cycle(channel: int, value: int) -> None`

Define duty cycle por valor absoluto (0–4095). Veja a versão do driver.

#### `set_duty_cycle_percent(channel: int, percent: float) -> None`

Define duty cycle em percentual (0.0–100.0%).

---

#### `set_pulse_us(channel: int, pulse_us: int) -> None`

Controla um canal diretamente pela **largura de pulso em microssegundos**, convertendo automaticamente para o tick equivalente com base na frequência configurada (50 Hz por padrão).

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `channel` | `int` | Canal PWM (0–15). |
| `pulse_us` | `int` | Largura de pulso em microssegundos. Ex.: `1500` para a posição neutra de um servo. |

---

#### `set_all_pwm(on: int, off: int) -> None`

Define ON/OFF para todos os canais. Veja a versão do driver.

#### `get_pwm(channel: int) -> tuple[int, int]`

Lê o estado atual de um canal. Veja a versão do driver.

#### `reset_channel(channel: int) -> None`

Zera um canal específico.

#### `reset_all_channels() -> None`

Zera todos os canais.

#### `close() -> None`

Fecha o driver e o barramento I2C.

---

### Servo

Localização: `pca9685/servos.py`

Abstração para um servo convencional de **0° a 180°** — ideal para o pan/tilt da câmera do rover.

#### `Servo(pca: PCAServos, channel: int, min_pulse_us=500, max_pulse_us=2500)`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `pca` | `PCAServos` | Instância já inicializada do controlador. |
| `channel` | `int` | Canal ao qual o servo está fisicamente conectado (0–15). |
| `min_pulse_us` | `int` | Largura de pulso correspondente a 0°. Padrão: `500` µs. |
| `max_pulse_us` | `int` | Largura de pulso correspondente a 180°. Padrão: `2500` µs. |

> Ajuste `min_pulse_us`/`max_pulse_us` conforme o datasheet do seu servo específico — servos diferentes podem ter faixas de pulso levemente diferentes.

---

#### Propriedade `angle`

```python
servo.angle = 90     # move o servo para 90°
atual = servo.angle  # lê o último ângulo definido
```

| Operação | Tipo | Descrição |
|---|---|---|
| Atribuição (`set`) | `float` | Ângulo desejado (0.0 a 180.0°). Valores fora da faixa são automaticamente limitados (*clamped*). |
| Leitura (`get`) | `float \| None` | Último ângulo definido, ou `None` se o servo nunca foi movido ou está `detach()`-ado. |

#### `center() -> None`

Move o servo para 90° (posição central).

#### `detach() -> None`

Desativa o sinal PWM do canal, parando de forçar uma posição (o servo pode ficar "solto").

---

### ContinuousServo

Localização: `pca9685/servos.py`

Abstração para servos de **rotação contínua (360°)**, geralmente usados em rodas ou esteiras do rover, onde não existe um "ângulo final" — apenas velocidade e direção.

#### `ContinuousServo(pca, channel, min_pulse_us=500, max_pulse_us=2500, neutral_pulse_us=1500)`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `pca` | `PCAServos` | Instância já inicializada do controlador. |
| `channel` | `int` | Canal ao qual o servo está conectado (0–15). |
| `min_pulse_us` | `int` | Pulso para velocidade máxima em sentido reverso. Padrão: `500` µs. |
| `max_pulse_us` | `int` | Pulso para velocidade máxima em sentido de avanço. Padrão: `2500` µs. |
| `neutral_pulse_us` | `int` | Pulso correspondente à parada total. Padrão: `1500` µs. |

---

#### Propriedade `throttle`

```python
motor.throttle = 0.5    # 50% de velocidade, avançando
motor.throttle = -1.0   # velocidade máxima, revertendo
atual = motor.throttle  # lê o throttle atual
```

| Operação | Tipo | Descrição |
|---|---|---|
| Atribuição (`set`) | `float` | Valor de `-1.0` (reverso máximo) a `+1.0` (avanço máximo). `0.0` = parado. Fora da faixa é automaticamente limitado. |
| Leitura (`get`) | `float` | Último throttle definido. |

#### `stop() -> None`

Equivalente a `throttle = 0.0` — para o motor mantendo o sinal neutro.

#### `detach() -> None`

Desativa completamente o sinal PWM do canal (diferente de `stop()`, que mantém um pulso neutro ativo).

---

## Exceções

Definidas em `pca9685/driver.py`, todas derivam de `PCA9685Error`:

| Exceção | Quando ocorre |
|---|---|
| `PCA9685Error` | Classe base — pode ser usada para capturar qualquer erro da biblioteca. |
| `I2CError` | Falha de comunicação I2C (fiação solta, endereço incorreto, chip não respondeu). |
| `InvalidChannelError` | Canal informado fora da faixa 0–15. |
| `InvalidFrequencyError` | Frequência informada fora da faixa 24–1526 Hz. |

Exemplo de tratamento:

```python
from pca9685 import PCAServos
from pca9685.driver import I2CError, InvalidChannelError

try:
    pca = PCAServos()
    pca.set_pwm(channel=20, on=0, off=300)
except InvalidChannelError as e:
    print(f"Canal inválido: {e}")
except I2CError as e:
    print(f"Falha de comunicação: {e}")
```

---

## Testes

Os testes unitários usam um **mock** do `smbus2` (`tests/mock_smbus2.py`), simulando os registradores do chip em um dicionário Python. Isso permite validar toda a lógica matemática (cálculo de prescale, conversão de ângulo, duty cycle, throttle) **sem precisar de uma Raspberry Pi ou do PCA9685 físico conectado**.

```bash
python -m pytest tests/ -v
```

Resultado esperado:

```
============================== 39 passed in 0.61s ==============================
```

Para testar com hardware real conectado, veja `examples/teste_conexao.py` (verifica apenas a comunicação) e `examples/camera_pantilt.py` (movimenta servos de fato).

---

## Conexões físicas (hardware)

| Raspberry Pi 5 (pino físico) | Função | PCA9685 |
|---|---|---|
| Pino 1 | 3.3V | VCC |
| Pino 3 | GPIO2 (SDA1) | SDA |
| Pino 5 | GPIO3 (SCL1) | SCL |
| Pino 6 | GND | GND |

> **Importante:** os servos devem ser alimentados por uma fonte **externa** de 5–6V conectada ao terminal `V+` do PCA9685 — nunca pelo pino 5V da Raspberry Pi, sob risco de brownout e reinicialização inesperada.

Para verificar se o chip está sendo detectado corretamente no barramento:

```bash
sudo apt install i2c-tools -y
i2cdetect -y 1
```

O endereço `40` deve aparecer na tabela exibida.

---

## Notas e boas práticas

- Sempre chame `close()` (ou use `with PCAServos() as pca:`) ao final do uso, para garantir que os canais sejam zerados e o barramento I2C seja liberado corretamente.
- Para servos digitais que aceitem frequências diferentes de 50 Hz, ajuste o parâmetro `frequency` ao instanciar `PCAServos` — mas lembre-se de que essa frequência é **global**, aplicada a todos os canais simultaneamente.
- Os valores de `min_pulse_us` e `max_pulse_us` variam entre modelos de servo. Consulte o datasheet do servo específico se notar que ele não atinge os extremos esperados (0°/180° ou velocidade máxima).
- Use `detach()` quando quiser liberar fisicamente um servo (deixá-lo "solto") em vez de mantê-lo travado em uma posição — isso reduz consumo de energia e aquecimento do motor.
