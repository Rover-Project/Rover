# RoverLib

Biblioteca Python educacional para programar o **Rover**, robô do Projeto ROVER (UFPI) baseado em Raspberry Pi 5: controle das rodas, câmera, visão computacional e sensores em comandos simples.

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.move.forward(speed=50, duration=2)
    frame = rover.camera.get_frame()
    if rover.lidar.is_obstacle(30):
        rover.move.stop()
```

O mesmo código roda **no PC** (motores simulados e webcam) e **no Rover** (GPIO, Picamera2, Lidar TF-Luna).

## Início rápido

```bash
pip install roverlib[cli]
rover new meu_projeto
cd meu_projeto
rover run
```

Extras opcionais: `roverlib[ai]` (YOLOv8 e MediaPipe) e `roverlib[dev]` (pytest, black, ruff).

## Links

- Documentação: https://rover-project.github.io/Rover/
- Código-fonte e exemplos: https://github.com/Rover-Project/Rover
