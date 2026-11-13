# Configuração (`config.yaml`)

O `config.yaml` descreve o hardware do Rover. `Rover.from_config("config.yaml")` cria **apenas os componentes cujas seções estão presentes**:

| Seção | Componente | Acesso |
|---|---|---|
| `motors:` | motores (ponte-H L298N) | `rover.move` |
| `camera:` | Picamera2 ou webcam | `rover.camera` |
| `lidar:` | Lidar TF-Luna | `rover.lidar` |
| `pan_tilt:` | servos da câmera (PAN 360°, TILT 180°) | `rover.pan_tilt` |

Uma seção vazia (por exemplo, só `camera:`) usa os valores padrão.

## Exemplo completo

```yaml
motors:
  right: [17, 26]
  left: [25, 16]
  calibration:
    right: 1
    left: 1
  pwm_frequency: 1000
  simulate: auto

camera:
  width: 640
  height: 480
  fps: 30
  index: 0
  webcam: auto
  vertical_flip: false
  horizontal_flip: false
  brightness: 0.0
  contrast: 1.0
  saturation: 1.0

lidar:
  port: /dev/ttyAMA0
  baudrate: 115200
  simulate: auto
  simulated_distance: 200

pan_tilt:
  address: 0x40
  simulate: auto
  pan:
    channel: 0
    trim: 0
    invert: true
    min: -50
    max: 50
    degrees_per_second: [125, 100]
    calibration_speed: 20
  tilt:
    channel: 1
    min: 45
    max: 135
    center: 90
    invert: false
```

## `motors`

| Opção | Padrão | Descrição |
|---|---|---|
| `right` | `[17, 26]` | Pinos GPIO (numeração BCM) ligados às entradas IN3 e IN4 da ponte-H (motor direito) |
| `left` | `[25, 16]` | Pinos GPIO ligados às entradas IN1 e IN2 (motor esquerdo) |
| `calibration.right` / `calibration.left` | `1` | Multiplicam a velocidade de cada lado. Se o Rover puxa para a esquerda em `forward()`, o motor direito está mais rápido: reduza `calibration.right` (ex.: `0.95`) |
| `pwm_frequency` | `1000` | Frequência do PWM, em Hz |
| `simulate` | `auto` | `auto`: simula quando não há GPIO (PC). `true`: sempre simula. `false`: exige o hardware e gera erro se a GPIO não estiver disponível |

A variável de ambiente `ROVER_SIMULATE=1` força a simulação sem alterar o arquivo.

## `camera`

| Opção | Padrão | Descrição |
|---|---|---|
| `width`, `height` | `640`, `480` | Tamanho dos frames, em pixels |
| `fps` | `30` | Quadros por segundo |
| `index` | `0` | Qual câmera usar, se houver mais de uma |
| `webcam` | `auto` | `auto`: Picamera2 na Raspberry Pi, webcam no PC. `true`: sempre webcam. `false`: exige a Picamera2 |
| `vertical_flip`, `horizontal_flip` | `false` | Espelham a imagem. Com a câmera de cabeça para baixo, use os dois como `true` |
| `brightness`, `contrast`, `saturation` | — | Ajustes de imagem (apenas Picamera2; ignorados na webcam) |

Se a câmera não puder ser iniciada (por exemplo, PC sem webcam), aparece um aviso e o programa continua; usar `rover.camera` gera um erro explicando a falha.

## `lidar`

| Opção | Padrão | Descrição |
|---|---|---|
| `port` | `/dev/ttyAMA0` | Porta serial onde o TF-Luna está ligado |
| `baudrate` | `115200` | Velocidade da comunicação serial |
| `simulate` | `auto` | `auto`: simula quando o `pyserial` ou a porta não existem (PC). `true`: sempre simula. `false`: exige o sensor |
| `simulated_distance` | `200` | Distância, em cm, informada pelo Lidar simulado. Mude durante o programa com `rover.lidar.set_distance(cm)` |

Assim como a câmera, uma falha ao iniciar o Lidar real vira um aviso, e o restante do Rover continua funcionando.

## `pan_tilt`

Os dois servos que movem a câmera, ligados a um PCA9685 (I²C).

| Opção | Padrão | Descrição |
|---|---|---|
| `address` | `0x40` | Endereço I²C do PCA9685 |
| `simulate` | `auto` | `auto`: simula quando não há I²C (PC). `true`: sempre simula. `false`: exige o hardware |
| `pan.channel` | `0` | Canal do PCA9685 do servo **PAN** (horizontal, **360°**, rotação contínua) |
| `pan.trim` | `0` | Velocidade (-1.0 a 1.0) em que o PAN fica realmente parado. Ajuste se a câmera girar devagar sozinha após `stop_pan()` (ex.: `0.03`) |
| `pan.invert` | `false` | Inverte o sentido, se `pan_right()` girar para a esquerda |
| `pan.min`, `pan.max` | `-50`, `50` | Limites do giro, em graus (0° = câmera de frente; positivo = direita). O PAN para sozinho ao chegar neles. No Rover, protegem o cabo flat da câmera |
| `pan.degrees_per_second` | `125` | Graus por segundo do PAN na velocidade `calibration_speed`. Um número ou `[direita, esquerda]`, se um sentido for mais rápido. Usado para estimar a posição: meça no seu Rover |
| `pan.calibration_speed` | `20` | Velocidade (0 a 100) usada na medição acima; é também a velocidade padrão de `pan_to()` |
| `pan.pulse` | `[500, 2500]` | Pulsos mínimo e máximo do servo, em µs |
| `tilt.channel` | `1` | Canal do servo **TILT** (vertical, **180°**, posição) |
| `tilt.min`, `tilt.max` | `0`, `180` | Limites de ângulo, para não forçar o suporte da câmera |
| `tilt.center` | `90` | Ângulo com a câmera olhando para frente (usado por `center()`) |
| `tilt.invert` | `false` | Inverte o sentido, se `tilt_up()` abaixar a câmera |
| `tilt.hold` | `true` | Ao encerrar, o TILT continua segurando a câmera no centro (sem sinal, o peso da câmera a faria cair) |
| `tilt.pulse` | `[500, 2500]` | Pulsos mínimo e máximo do servo, em µs |

!!! note "Como o PAN sabe onde está?"
    O servo de 360° gira continuamente e não informa sua posição: ele é controlado por **velocidade** (como as rodas). O `PanTilt` **estima** o ângulo multiplicando a velocidade pelo tempo de giro, considerando que o programa começa com a câmera de frente (0°). É assim que ele respeita `pan.min`/`pan.max`, e que `pan_to()`, `pan_degrees()` e `center()` funcionam. Ao encerrar, a câmera volta para a frente. Se a estimativa se perder, alinhe a câmera e chame `reset_pan_position()`.

    Para medir `degrees_per_second`: com a câmera em um limite, gire com velocidade 20 até o outro limite e cronometre; divida o ângulo entre os limites pelo tempo. Repita no outro sentido.

## Formato antigo dos exemplos

Os exemplos da pasta `examples/` usam os motores dentro de `gpio: motor:`. `Rover.from_config` também aceita esse formato:

```yaml
gpio:
  motor:
    right: [17, 26]
    left: [25, 16]
    calibration:
      right: 1
      left: 1
```

## Lendo outras configurações

Para guardar parâmetros do seu próprio programa (velocidades, ganhos do PID…) no mesmo arquivo, use `Config`:

```python
from roverlib import Config

config = Config("config.yaml")
pid = config.get("pid")      # ex.: {"kp": 0.4, "ki": 0, "kd": 0.1}
```
