# Meu Projeto Rover

Projeto criado com `rover new`, da [RoverLib](https://github.com/Rover-Project/Rover).

## Estrutura

```
meu_projeto/
├── main.py          # programa principal: comece por aqui
├── config.yaml      # pinos dos motores, câmera e Lidar
└── src/
    └── examples/    # exemplos curtos para estudar e adaptar
```

## Executando

```bash
rover run                         # executa o main.py (dentro da pasta do projeto)
rover run meu_projeto             # ou indicando a pasta
```

No PC, os motores são **simulados**: os comandos aparecem no terminal e a câmera usa a webcam.
Na Raspberry Pi, o mesmo código move o Rover de verdade.

Para testar na Raspberry Pi sem mover as rodas:

```bash
ROVER_SIMULATE=1 rover run
```

## Exemplos

Execute dentro da pasta do projeto:

| Comando | O que faz | Precisa de |
|---|---|---|
| `python -m src.examples.quadrado` | Percorre um quadrado | motores |
| `python -m src.examples.cor_vermelha` | Destaca objetos vermelhos na imagem | seção `camera:` |
| `python -m src.examples.parar_no_obstaculo` | Anda e para perto de obstáculos | seção `lidar:` |

## Comandos principais

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.move.forward(50, duration=2)     # frente (velocidade 0-100, tempo em s)
    rover.move.backward(50, duration=2)    # trás
    rover.move.turn_left(50, duration=1)   # gira para a esquerda
    rover.move.turn_right(50, duration=1)  # gira para a direita
    rover.move.move(speed_right=60, speed_left=30)  # cada lado com sua velocidade
    rover.move.stop()

    frame = rover.camera.get_frame()       # imagem (array NumPy, BGR)

    rover.lidar.get_distance()             # distância em cm
    rover.lidar.is_obstacle(30)            # True se houver algo a 30 cm ou menos

    rover.pan_tilt.pan_right(30, duration=0.5)  # gira a câmera (servo 360°)
    rover.pan_tilt.tilt_to(60)             # inclina a câmera (servo 180°)
    rover.pan_tilt.center()
```
