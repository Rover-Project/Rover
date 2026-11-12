# Plugins

Plugins são os **drivers de hardware** da RoverLib: cada um encapsula uma peça (motor, câmera, sensor, servo) e esconde o protocolo usado por ela (GPIO/PWM, UART, I²C, libcamera). As camadas de cima (`Robot`, `PanTilt`, `Rover`) são construídas sobre eles.

| Plugin | Hardware | Versão simulada | API pública |
|---|---|---|---|
| [`pin`](pin/) | GPIO e PWM da Raspberry Pi (C++/pybind11) | — (base dos outros) | `Pin`, `PinMode` |
| [`motor`](motor/) | motor DC + ponte-H L298N | `VirtualMotor` | `MotorDriver`, `VirtualMotor` |
| [`camera`](camera/) | Picamera2 / Camera Module 3 | `Webcam` (PC) | `open_camera`, `Camera`, `AfCamera`, `Webcam` |
| [`lidar`](lidar/) | Lidar TF-Luna (UART) | `VirtualLidar` | `Lidar`, `VirtualLidar` |
| [`PCAServos`](PCAServos/) | servos via PCA9685 (I²C) | `VirtualServo`, `VirtualContinuousServo` | `PCAServos`, `Servo`, `ContinuousServo` |

---

## Padrão de um plugin

Todo plugin segue a mesma estrutura:

```
plugins/<nome>/
├── __init__.py      # API pública (o que o usuário importa)
├── README.md        # documentação do plugin (seções abaixo)
├── <driver>.py      # driver real: import tolerante + HARDWARE_AVAILABLE
├── virtual.py       # versão simulada, com a mesma interface (quando fizer sentido)
├── interface.py     # (opcional) classe abstrata, quando há mais de uma implementação
├── exceptions.py    # exceções do plugin
├── examples/        # (opcional) scripts manuais para testar o hardware
└── tests/
    └── test_<driver>.py
```

> Alguns arquivos antigos ainda usam camelCase (`motorDriver.py`, `cameraInterface.py`). A padronização dos nomes para snake_case será feita depois, de uma vez, mantendo os caminhos antigos funcionando.

### 1. API pública no `__init__.py`

O usuário importa do pacote, não do arquivo interno:

```python
from roverlib.plugins.lidar import Lidar, VirtualLidar, HARDWARE_AVAILABLE
```

O `__init__.py` reexporta as classes e define `__all__`. Assim, a organização interna pode mudar sem quebrar quem usa o plugin.

### 2. Import tolerante e `HARDWARE_AVAILABLE`

Importar o plugin **nunca pode falhar** por falta de hardware: o módulo carrega no PC e só o uso do hardware gera erro.

```python
try:
    import serial                   # biblioteca que só funciona com o hardware
    HARDWARE_AVAILABLE = True
except ImportError:
    serial = None
    HARDWARE_AVAILABLE = False


class MeuSensor:
    def __init__(self):
        if not HARDWARE_AVAILABLE:
            raise MeuSensorNotAvailable("explique o que falta e como resolver")
```

### 3. Versão simulada (`virtual.py`)

Se o plugin é usado pelo `Rover`, ele tem uma versão simulada com **os mesmos métodos públicos** do driver real. Ela permite desenvolver e testar no PC. A decisão entre real e simulado fica em `roverlib.utils.simulation.resolve_simulate()`, que respeita `simulate=True/False` e a variável `ROVER_SIMULATE=1`.

### 4. Exceções (`exceptions.py`)

Toda exceção herda de `RoverLibError` (de `roverlib.exceptions`), além da exceção padrão do Python que faz sentido:

```python
from roverlib.exceptions import RoverLibError, HardwareNotAvailable

class MeuSensorNotAvailable(HardwareNotAvailable):          # também é RuntimeError
    """Biblioteca ou hardware do sensor indisponível."""

class LeituraInvalida(RoverLibError, ValueError):
    """Valor fora do esperado."""
```

Assim o aluno pode tratar qualquer erro da biblioteca com `except RoverLibError`, e códigos antigos que tratavam `RuntimeError`/`ValueError` continuam funcionando.

### 5. Testes (`tests/`)

- Rodam **no PC**: o hardware é substituído por falsos (`unittest.mock`, `monkeypatch`).
- Testes que exigem a Raspberry Pi levam `@pytest.mark.hardware` e ficam fora da execução padrão.
- Nada de alterar `sys.path`: importe sempre por `roverlib.plugins.<nome>`.

```bash
python -m pytest                    # PC (padrão)
python -m pytest -m hardware        # Raspberry Pi
```

### 6. README

Seções: **Hardware** (modelo, especificações) · **Ligação** (pinos) · **Uso** (exemplo curto) · **Simulação** · **Exceções** · **Testes**.

---

## Checklist para um plugin novo

- [ ] Pasta `plugins/<nome>/` com `__init__.py` exportando a API e `__all__`
- [ ] Driver importável no PC, com `HARDWARE_AVAILABLE`
- [ ] `exceptions.py` com exceções herdando de `RoverLibError`
- [ ] `virtual.py` com a mesma interface, se o plugin for usado pelo `Rover`
- [ ] `tests/` rodando no PC; testes de hardware marcados com `@pytest.mark.hardware`
- [ ] `README.md` com as seções do padrão
- [ ] Se for usado pelo `Rover`: seção no `config.yaml` (`Rover.from_config`), página em `docs/api/` e em `docs/configuracao.md`
