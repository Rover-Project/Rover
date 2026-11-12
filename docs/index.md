# RoverLib

A **RoverLib** é uma biblioteca Python educacional para programar o **Rover**, robô do Projeto ROVER (*Robotic Optical Vehicle for Embedded Recognition*) do Departamento de Computação da UFPI, baseado em Raspberry Pi 5.

Ela reúne em comandos simples o controle das rodas, a captura e o processamento de imagens e a leitura de sensores, para que estudantes e professores possam se concentrar nos conceitos de robótica, visão computacional e inteligência artificial, e não nos detalhes de GPIO, PWM ou protocolos seriais.

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.move.forward(speed=50, duration=2)       # anda 2 segundos

    frame = rover.camera.get_frame()               # captura uma imagem

    if rover.lidar.is_obstacle(30):                # algo a menos de 30 cm?
        rover.move.stop()

    rover.pan_tilt.tilt_to(60)                     # inclina a câmera
```

## Destaques

- **Mesmo código no PC e no Rover.** Sem a Raspberry Pi, os motores são simulados e a câmera usa a webcam: dá para aprender e testar em qualquer computador.
- **Configuração em um arquivo.** Pinos, calibração, câmera e Lidar ficam no `config.yaml`, fora do código.
- **Projetos prontos para começar.** `rover new meu_projeto` cria um projeto com exemplos; `rover run` o executa.
- **Visão computacional incluída.** Segmentação por cor, detecção de círculos e de linhas com OpenCV.
- **Câmera móvel.** Os servos do pan-tilt giram e inclinam a câmera com comandos como `pan_right()` e `tilt_to()`.
- **Mensagens claras.** Erros explicam o que falta, como *"Adicione a seção 'camera:' ao config.yaml"*.

## Comece por aqui

```bash
pip install roverlib[cli]
rover new meu_projeto
cd meu_projeto
rover run
```

1. [Instalação](instalacao.md): no PC e na Raspberry Pi.
2. [Primeiro projeto](primeiro-projeto.md): tutorial de 10 minutos, sem precisar do robô.
3. [Configuração](configuracao.md): todas as opções do `config.yaml`.
4. [Exemplos](exemplos.md): seguir linha, seguir bola, câmera que acompanha objetos, desviar de obstáculos, YOLO e outros.
5. [Arquitetura](arquitetura.md): como a biblioteca é organizada e como estendê-la.
6. [Referência da API](api/rover.md): todos os comandos, gerada a partir do código.

## Hardware do Rover

| Componente | Modelo | Plugin |
|---|---|---|
| Computador | Raspberry Pi 5 | — |
| Motores DC | ponte-H L298N | `plugins/motor` |
| Câmera | Raspberry Pi Camera (Picamera2), Camera Module 3 com foco | `plugins/camera` |
| Distância | Lidar TF-Luna (UART) | `plugins/lidar` |
| Servos da câmera (pan-tilt) | PAN 360° + TILT 180° via PCA9685 (I²C) | `modules/pan_tilt`, `plugins/PCAServos` |

## Código aberto

O código e esta documentação estão no [GitHub](https://github.com/Rover-Project/Rover), sob a licença MIT. Sugestões e problemas podem ser relatados nas *issues* do repositório.
