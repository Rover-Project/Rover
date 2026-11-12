# Arquitetura

A RoverLib é organizada em camadas. As de baixo conversam com o hardware; as de cima oferecem comandos simples para quem programa o Rover. Quem usa a biblioteca normalmente só precisa da camada mais alta, a classe `Rover`.

```
┌──────────────────────────────────────────────────────────────────┐
│  Projeto do usuário     main.py + config.yaml + src/             │  criado por `rover new`
└───────────────┬──────────────────────────────────────────────────┘
                │ Rover.from_config("config.yaml")
┌───────────────▼──────────────────────────────────────────────────┐
│  Rover (rover.py)   rover.move · .camera · .lidar · .pan_tilt    │  ponto de entrada
├──────────────────────────────────────────────────────────────────┤
│  modules/               comportamento e inteligência             │
│   ├ movement/   Robot, PID, Calibration                          │
│   ├ pan_tilt/   PanTilt (servos da câmera: PAN 360°, TILT 180°)  │
│   ├ vision/     VisionModule (círculos, linha, obstáculo)        │
│   └ processing/ ProcessingImage (recorte, gama, cor, bordas)     │
├──────────────────────────────────────────────────────────────────┤
│  plugins/               drivers, um por peça de hardware         │
│   ├ motor/      MotorInterface → MotorDriver | VirtualMotor      │
│   ├ camera/     CameraInterface → Camera | AfCamera | Webcam     │
│   ├ lidar/      Lidar (TF-Luna via UART)                         │
│   ├ PCAServos/  Servo | ContinuousServo | Virtual* (PCA9685)     │
│   └ pin/        Pin: GPIO e PWM em C++ (pybind11)                │
├──────────────────────────────────────────────────────────────────┤
│  cli/ + core/           comando `rover` (new, run, hello)        │  ferramentas
│  utils/                 Config (leitura do config.yaml)          │
└───────────────┬──────────────────────────────────────────────────┘
                ▼
        Raspberry Pi 5: GPIO, UART, I²C, câmera CSI/USB
```

## Camadas

### Plugins: drivers de hardware

Cada plugin encapsula **uma peça de hardware** e esconde o protocolo usado por ela (PWM, UART, I²C, libcamera).

- **`pin`** é a base de tudo que usa GPIO. É um módulo nativo em C++ (pybind11) com escrita digital, PWM por hardware e PWM por software. Os drivers de motor e de servo são construídos sobre ele.
- **`motor`** controla um motor DC ligado a uma ponte-H L298N. `MotorDriver` escreve nos pinos de verdade; `VirtualMotor` apenas registra e imprime os comandos.
- **`camera`** captura frames. `Camera` usa a Picamera2 (Raspberry Pi); `AfCamera` acrescenta controle de foco (Camera Module 3); `Webcam` usa o OpenCV (PC ou câmera USB).
- **`lidar`** lê o TF-Luna em uma thread em segundo plano e mantém sempre a última medida disponível.
- **`PCAServos`** controla servos por um PCA9685 (I²C), com as bibliotecas da Adafruit: `Servo` (posição, 0–180°) e `ContinuousServo` (rotação contínua). `VirtualServo` e `VirtualContinuousServo` são as versões simuladas.

Plugins do mesmo tipo seguem uma **interface comum** (`MotorInterface`, `CameraInterface`). É isso que permite trocar o motor real pelo simulado, ou a Picamera2 pela webcam, sem mudar o código que os utiliza.

### Módulos: comportamento e inteligência

Os módulos combinam plugins em operações com significado para o aluno:

- **`Robot`** cria dois drivers de motor e oferece `forward()`, `backward()`, `turn_left()`, `turn_right()`, `move()` (velocidade por lado) e `turn_degrees()`, aplicando a calibração de cada lado.
- **`PanTilt`** move a câmera com dois servos: o **PAN** (horizontal) é um servo de 360°, controlado por velocidade e tempo, como as rodas; o **TILT** (vertical) é um servo de 180°, controlado por ângulo, com limites para proteger o suporte.
- **`PID`** implementa os controladores P, PD e PID usados nos exemplos de seguir linha e seguir objetos.
- **`ProcessingImage`** e **`VisionModule`** são funções de visão computacional clássica (OpenCV): recebem um frame em BGR e devolvem máscaras, círculos detectados ou o desvio de uma linha. Não dependem de nenhuma câmera específica.

### Rover: ponto de entrada

`Rover.from_config("config.yaml")` lê a configuração e cria somente os componentes presentes no arquivo:

| Seção do `config.yaml` | Componente criado | Acesso |
|---|---|---|
| `motors:` | `Robot` | `rover.move` |
| `camera:` | `Camera` ou `Webcam` (via `open_camera()`) | `rover.camera` |
| `lidar:` | `Lidar` | `rover.lidar` |
| `pan_tilt:` | `PanTilt` | `rover.pan_tilt` |

O `Rover` não acrescenta lógica de controle; ele **monta e entrega** os componentes das camadas de baixo. Assim, tudo que se aprende usando `rover.move` vale também para quem usar `Robot` diretamente.

### Ferramentas: CLI e configuração

- `rover new <nome>` copia o template de projeto (`main.py`, `config.yaml`, exemplos).
- `rover run [pasta]` executa o `main.py` com o Python do ambiente atual, a partir da pasta do projeto.
- `Config` lê e grava o `config.yaml`, inclusive parâmetros próprios do programa do usuário.

## Decisões de projeto

**Mesmo código no PC e no Rover.**
Sem GPIO, o `Robot` usa o `VirtualMotor`; sem I²C, o `PanTilt` usa servos virtuais; sem Picamera2, `open_camera()` usa a webcam. O aluno desenvolve e testa a lógica no computador e leva o mesmo projeto para o robô. A simulação também pode ser forçada (`simulate: true` ou `ROVER_SIMULATE=1`) para testar na Raspberry Pi sem mover as rodas nem os servos.

**Configuração fora do código.**
Pinos, calibração e parâmetros da câmera ficam no `config.yaml`. Trocar a fiação ou o Rover não exige alterar o programa.

**Mensagens de erro voltadas ao aluno.**
Usar um componente não configurado gera, por exemplo, *"rover.camera não foi configurado. Adicione a seção 'camera:' ao config.yaml."*. Uma falha ao iniciar a câmera ou o Lidar vira um aviso, e o resto do Rover continua funcionando.

**Liberação de recursos garantida.**
`Rover`, `Robot`, `PanTilt` e `Lidar` funcionam com `with`: ao sair do bloco, inclusive por erro ou Ctrl+C, os motores param e as portas são fechadas.

**Importação sob demanda.**
`from roverlib import Rover` não carrega OpenCV, câmera nem GPIO até que sejam usados. Isso mantém o `rover hello` e o `rover new` rápidos e permite usar partes da biblioteca sem todas as dependências.

## Fluxo de um programa

Um laço típico de "seguir um objeto" passa pelas camadas assim:

```
rover.camera.get_frame()                       plugin de câmera  → frame (BGR)
        ↓
ProcessingImage.color_segmentation(frame)      processamento     → máscara da cor
VisionModule.houghCircleDetect(mascara)        visão             → (x, y, raio)
        ↓
erro = x - centro_da_imagem
correcao = pid.controller_P(erro)              controle          → ajuste de velocidade
        ↓
rover.move.move(speed_right=..., speed_left=...)   Robot         → velocidade por lado
        ↓
MotorDriver.set_movement(...) → Pin.pwm(...)   plugins motor/pin → sinal PWM na GPIO
```

Os exemplos `folowCircle` e `lineDetect` seguem esse fluxo com as rodas; o `cameraTracking` faz o mesmo movendo só a câmera, com `rover.pan_tilt`. Veja [Exemplos](exemplos.md).

## Estrutura de diretórios

```
roverlib/src/roverlib/
├── __init__.py          # atalhos: from roverlib import Rover, Robot, ...
├── rover.py             # classe Rover
├── cli/                 # comando `rover` e template do `rover new`
├── core/                # execução de projetos (rover run)
├── modules/
│   ├── movement/        # Robot, PID, Calibration
│   ├── pan_tilt/        # PanTilt
│   ├── processing/      # ProcessingImage
│   └── vision/          # VisionModule
├── plugins/
│   ├── camera/          # Camera, AfCamera, Webcam, open_camera
│   ├── lidar/           # Lidar
│   ├── motor/           # MotorDriver, VirtualMotor
│   ├── pin/             # GPIO/PWM nativo (C++)
│   └── PCAServos/       # servos via PCA9685 (e simulados)
├── utils/               # Config, modo simulação
└── tests/               # testes da classe Rover
```

Cada plugin e módulo tem um `README.md` próprio com detalhes de hardware e exemplos, e testes em uma pasta `tests/` ao lado do código.

## Estendendo a biblioteca

Para adicionar um novo sensor ou atuador:

1. Crie o driver em `plugins/<sensor>/`, com métodos `start()`/`stop()` e leituras de alto nível (como `get_distance()` no Lidar).
2. Se o sensor tiver variantes, defina uma interface comum, como `MotorInterface`.
3. Escreva testes que simulem o hardware (veja `plugins/lidar/tests/`, que simula a porta serial).
4. Para disponibilizá-lo pelo `Rover`, adicione a seção correspondente em `Rover.__init__` e em `from_config`, e documente a seção em [Configuração](configuracao.md).
