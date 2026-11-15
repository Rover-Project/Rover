# Configuração e erros

## Config

Lê e grava arquivos YAML, como o `config.yaml` do projeto. O `Rover.from_config()` já lê as seções do hardware; use `Config` para os parâmetros do seu próprio programa. Veja [Configuração](../configuracao.md) para as seções reconhecidas.

::: roverlib.utils.config_manager.Config

## Exceções

Todas as exceções da RoverLib herdam de `RoverLibError` e também da exceção padrão do Python correspondente. Assim, um único `except RoverLibError` trata qualquer problema do Rover.

| Exceção | Herda de | Quando acontece |
|---|---|---|
| `ComponentNotAvailable` | `RoverLibError`, `RuntimeError` | Uso de `rover.camera`, `rover.lidar`... sem a seção no `config.yaml`, ou com falha ao iniciar |
| `HardwareNotAvailable` | `RoverLibError`, `RuntimeError` | Hardware exigido, mas ausente (base das exceções abaixo) |
| `PinNotAvailable` | `HardwareNotAvailable` | Módulo de GPIO indisponível (PC, ou não compilado na Raspberry Pi) |
| `MotorCreationError` | `HardwareNotAvailable`, `ImportError` | Motor real criado sem GPIO |
| `CameraNotAvailable` | `HardwareNotAvailable`, `ModuleNotFoundError` | Picamera2/libcamera ausentes |
| `LidarNotAvailable` | `HardwareNotAvailable`, `ModuleNotFoundError` | `pyserial` ausente |
| `PCANotAvailable` | `HardwareNotAvailable` | PCA9685 inacessível pelo I²C |
| `CameraNotStart` | `RoverLibError`, `RuntimeError` | Captura antes de `start()` |
| `AutofocusModeInvalid` | `RoverLibError`, `RuntimeError` | Comando de foco incompatível com o modo atual |
| `LidarNotStart`, `LidarDoNotRespond` | `RoverLibError`, `RuntimeError` | Lidar não iniciado ou sem resposta na porta serial |
| `UninitializedMotorError` | `RoverLibError`, `RuntimeError` | Motor usado antes de `initialize()` |
| `DirectionInvalidMotorError` | `RoverLibError`, `ValueError` | Sentido diferente de `FORWARD`, `BACKWARD` ou `STOP` |
| `ServoAngleError` | `RoverLibError`, `ValueError` | Ângulo de servo fora de 0–180° |

::: roverlib.exceptions.RoverLibError

::: roverlib.exceptions.HardwareNotAvailable

::: roverlib.rover.ComponentNotAvailable
