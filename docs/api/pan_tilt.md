# Pan-tilt da câmera

Dois servos movem a câmera do Rover, ligados a um PCA9685 (I²C):

| Eixo | Servo | Controle | Métodos |
|---|---|---|---|
| **PAN** (horizontal) | 360°, rotação contínua | velocidade e tempo | `pan()`, `pan_left()`, `pan_right()`, `pan_to()`, `pan_degrees()`, `stop_pan()` |
| **TILT** (vertical) | 180°, posição | ângulo | `tilt_to()`, `tilt_up()`, `tilt_down()`, `tilt_angle` |

Pelo `Rover`, é acessado como `rover.pan_tilt` (seção `pan_tilt:` do [config.yaml](../configuracao.md#pan_tilt)). Fora da Raspberry Pi, os servos são simulados.

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.pan_tilt.tilt_to(60, smooth=True)       # inclina suavemente para 60°
    rover.pan_tilt.pan_to(30)                     # gira até ~30° à direita (posição estimada)
    rover.pan_tilt.pan_left(20, duration=0.3)     # gira para a esquerda por 0,3 s
    rover.pan_tilt.center()
```

O exemplo `examples/cameraTracking` usa o pan-tilt para a câmera acompanhar um objeto vermelho.

::: roverlib.modules.pan_tilt.pan_tilt.PanTilt

## Drivers de servo

Usados internamente pelo `PanTilt`.

::: roverlib.plugins.PCAServos.pca9685.servos.PCAServos

::: roverlib.plugins.PCAServos.pca9685.servos.Servo

::: roverlib.plugins.PCAServos.pca9685.servos.ContinuousServo
