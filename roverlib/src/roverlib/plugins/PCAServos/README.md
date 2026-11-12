# Plugin PCAServos

Controle de servos ligados a um **PCA9685** (16 canais de PWM via I²C), usando as bibliotecas oficiais da Adafruit. No Rover, ele move os servos da câmera (pan-tilt).

> Em programas, prefira o [`PanTilt`](../../modules/pan_tilt/pan_tilt.py) (`rover.pan_tilt`), que usa este plugin e acrescenta limites de ângulo, *trim*, inversão de sentido e simulação no PC.

## Estrutura

```
PCAServos/
├── __init__.py        # API pública
├── exceptions.py      # PCANotAvailable, ServoAngleError
├── pca9685/
│   ├── servos.py      # PCAServos, Servo (180°), ContinuousServo (360°)
│   └── virtual.py     # VirtualServo, VirtualContinuousServo (simulação)
├── examples/          # scripts para testar o hardware
└── tests/
```

## Hardware

| Item | Valor no Rover |
|---|---|
| Controlador | PCA9685, endereço I²C `0x40`, barramento 1 |
| Frequência | 50 Hz (padrão de servos RC) |
| PAN (horizontal) | canal 0, servo de **rotação contínua (360°)** |
| TILT (vertical) | canal 1, servo de **posição (180°)** |

## Ligação

| PCA9685 | Raspberry Pi 5 |
|---|---|
| VCC | 3,3 V (lógica) |
| GND | GND |
| SDA | GPIO 2 (pino 3) |
| SCL | GPIO 3 (pino 5) |
| V+ | fonte externa de 5–6 V para os servos (não alimente servos pela Raspberry Pi) |

Ative o I²C (`sudo raspi-config` → *Interface Options* → *I2C*) e confira a placa:

```bash
i2cdetect -y 1     # deve aparecer "40"
```

## Uso

```python
from roverlib.plugins.PCAServos import PCAServos, Servo, ContinuousServo

with PCAServos(address=0x40) as pca:
    tilt = Servo(pca, channel=1)          # servo de posição
    tilt.angle = 60                       # 0 a 180°; fora disso gera ServoAngleError
    tilt.center()                         # 90°

    pan = ContinuousServo(pca, channel=0) # servo de rotação contínua
    pan.throttle = 0.3                    # velocidade de -1.0 a 1.0
    pan.stop()
```

| Classe | Controle | Métodos e propriedades |
|---|---|---|
| `PCAServos` | placa PCA9685 | `get_servo(channel)`, `close()`, uso com `with` |
| `Servo` | ângulo (0–180°) | `angle`, `center()`, `detach()` |
| `ContinuousServo` | velocidade (-1 a 1) | `throttle`, `stop()`, `detach()` |

`detach()` desliga o sinal do servo (sem torque).

## Simulação

Sem I²C (PC), o módulo continua importável e `HARDWARE_AVAILABLE` vale `False`. Criar um `PCAServos` gera `PCANotAvailable`. As classes `VirtualServo` e `VirtualContinuousServo` têm a mesma interface e são usadas automaticamente pelo `PanTilt` fora da Raspberry Pi.

## Exceções

| Exceção | Quando | Também é um |
|---|---|---|
| `PCANotAvailable` | bibliotecas/I²C ausentes ou placa não encontrada | `RuntimeError` |
| `ServoAngleError` | ângulo fora de 0–180° | `ValueError` |

Ambas herdam de `RoverLibError`.

## Testes

```bash
python -m pytest src/roverlib/plugins/PCAServos      # PC (sem hardware)
```

Na Raspberry Pi, para testar o hardware:

```bash
python src/roverlib/plugins/PCAServos/examples/teste_conexao.py    # comunicação I²C, sem mover
python src/roverlib/plugins/PCAServos/examples/camera_pantilt.py   # move o PAN e o TILT
```
