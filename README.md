# Rover: Plataforma de Robótica Autônoma com Code as Policies

## Apresentação

O **Rover** é uma plataforma de robótica de código aberto baseada em **Raspberry Pi 5**, projetada para implementar arquiteturas inovadoras de **Code as Policies**. O sistema permite que um operador humano defina objetivos em linguagem natural e um LLM (Large Language Model) gere automaticamente código Python executável que coordena todos os subsistemas robóticos.

O projeto moderniza um rover 1.0 original, substituindo seu sistema de controle por uma arquitetura totalmente modular em Python, com suporte a visão computacional híbrida, controle de motores DC em tempo real e orquestração por LLM.

---

## Características

- **Arquitetura Modular em Python:** Separação clara entre drivers, comportamento e inteligência.
- **Visão Computacional Clássica:** Algoritmos otimizados (Hough, Canny, HSV) rodando a 30 FPS na RPi 5.
- **Line-Following com PID:** Algoritmo de controle proporcional simplificado com detecção de obstáculos.
- **Compatibilidade Multiplataforma:** Fallback automático para câmera mock, permitindo desenvolvimento em PC.
- **Code as Policies:** Integração com LLMs para geração automática de comportamentos.

---

## Requisitos de Hardware

### Obrigatório
- **Raspberry Pi 5 Model B** (8 GB RAM recomendado)
- **Câmera Picamera2** (ou webcam USB como fallback)
- **Ponte-H L298N** para controle de motores DC
- **Bateria/Fonte:** 12V para motores, 5V para RPi

### Hardware para Testes (PC)
- Qualquer PC com Linux/macOS/Windows
- Câmera integrada ou USB

---

## Instalação Rápida

### Pré-requisitos
```bash
python --version  # Python 3.8+
pip --version     # pip 22.0+
```

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/Rover-Project/Rover.git
cd Rover
```

2. **Instale dependências Python:**
```bash
pip install -r requirements.txt
```

3. **Verifique instalação:**
```bash
python -c "from rover_lib import Rover; print('Rover importado com sucesso')"
```

---

## Configuração

### Para Raspberry Pi 5

#### 1. Habilitação da Câmera Picamera2

```bash
# No RPi, execute:
sudo raspi-config
# Navegue: Interfacing Options → Camera → Enable
```

#### 2. Configuração de Pinos GPIO

Edite `lib_rover/rover_lib/configs/config.yaml`:

```yaml
gpio:
  motor_esquerdo: [17, 27]    # [pino_direção, pino_PWM]
  motor_direito: [22, 23]

camera:
  resolution: [640, 480]
  fps: 30
  preview_resolution: [320, 240]
```

**Verificação de pinos:** Consulte diagrama GPIO da RPi 5. Os pinos padrão (17, 22, 23, 27) são válidos para modelos B comuns.

#### 3. Permissões de GPIO

```bash
sudo usermod -a -G gpio $USER
# Logout e login para aplicar mudanças
```

### Para Desenvolvimento em PC

Não é necessária configuração adicional. O sistema detecta automaticamente a ausência de `picamera2` e utiliza uma câmera mock com gradiente de teste.

```bash
# Teste:
python -c "from rover_lib import Rover; r = Rover(); print(r.camera)"
```

---

## Utilização

### Exemplo Básico: Avanço Simples

```python
from rover_lib import Rover
import time

rover = Rover()

# Move para frente por 3 segundos a velocidade 50
rover.movement.forward(speed=50, duration=3.0)

rover.stop_and_cleanup()
```

### Exemplo: Line-Following

```python
from rover_lib import Rover

rover = Rover()

# Inicia line-following com ganho proporcional 0.7
# Executa por 30 segundos
rover.follow_line(base_speed=30, kp=0.7, duration=30.0)

rover.stop_and_cleanup()
```

### Exemplo: Detecção de Círculos

```python
from rover_lib import Rover

rover = Rover()

# Captura um frame
frame = rover.camera.get_frame()

# Detecta círculos
circle = rover.vision.detect_circle(frame, color_range='red')

if circle:
    print(f"Círculo detectado em: x={circle['x']}, y={circle['y']}, raio={circle['radius']}")

rover.stop_and_cleanup()
```

---

## Estrutura de Diretórios

```
Rover/
├── lib_rover/                          # Biblioteca principal
│   ├── rover_lib/
│   │   ├── rover.py                   # Classe principal (Rover)
│   │   ├── configs/
│   │   │   └── config.yaml            # Configuração de GPIO e câmera
│   │   ├── modules/
│   │   │   ├── movement/              # Controle de motores (Robot, Motor)
│   │   │   ├── camera/                # Captura de câmera (CameraModule, Webcam)
│   │   │   ├── processing/            # Processamento de imagem
│   │   │   └── vision/                # Visão computacional (VisionModule)
│   │   └── utils/
│   │       └── config_manager.py      # Carregamento de configuração
│   └── setup.py
│
├── examples/
│   ├── circleDetect/                  # Exemplo: detecção de círculos
│   ├── roverTkControl/                # Exemplo: interface Tkinter de controle
│   └── ...
│
├── scripts_tests/
│   ├── camera/                        # Scripts de teste de câmera
│   ├── motor/                         # Scripts de teste de motores
│   └── object_detection/              # Testes de detecção (Hough, etc.)
│
├── docs/                              # Documentação Markdown
│   ├── index.md                       # Página inicial
│   ├── arquitetura.md                 # Documentação de arquitetura
│   └── api/
│       └── drivers.md                 # Referência de API
│
├── mkdocs.yml                         # Configuração de documentação
├── requirements.txt                   # Dependências Python
└── README.md                          # Este arquivo
```

---

## Exemplos de Uso

### Exemplo 1: Detecção de Círculos com Visualização

```bash
cd Rover/examples/circleDetect
python main.py
```

**O que acontece:**
- Câmera captura frames contínuos.
- Algoritmo de Hough detecta círculos.
- Visualiza círculos com marcadores (centro, raio).
- Imprime coordenadas na terminal.

### Exemplo 2: Interface Gráfica de Controle

```bash
cd Rover/examples/roverTkControl
python main.py
```

**Funcionalidade:**
- Botões de direção (↑ frente, ↓ trás, ← esquerda, → direita).
- Slider de velocidade (0–100%).
- Exibição de estado atual (velocidade, direção).

### Exemplo 3: Teste de Hough em Tempo Real

```bash
python Rover/scripts_tests/object_detection/HoughTransform/realTime/grayScale.py
```

**Parâmetros ajustáveis:**
```python
main(h=680, w=480, minDist=40, minRadius=10, maxRadius=120)
```

---

## Dependências

O arquivo `requirements.txt` especifica todas as dependências:

```
gpiozero          # Abstração de GPIO
Pillow            # Processamento de imagem
rpi.gpio          # GPIO para RPi (RPi apenas)
picamera2         # Câmera RPi (RPi apenas)
opencv-python     # Visão computacional (Hough, Canny, etc.)
numpy             # Álgebra linear
PyYAML            # Carregamento de configuração
```

**Dependências opcionais:**
- `mkdocs-material`: Para compilar documentação localmente (`mkdocs serve`).
- `ultralytics`: Para integração com YOLO (detecção avançada).
- `tflite-runtime`: Para modelos TensorFlow Lite (inferência em RPi).

---

## Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'picamera2'"

**Solução:** O sistema usa automaticamente câmera mock. Este aviso é esperado em PC. Se estiver em RPi, execute:

```bash
sudo apt-get install -y python3-picamera2
```

### Problema: "PermissionError: GPIO requires root privileges"

**Solução:** Adicione o usuário ao grupo `gpio`:

```bash
sudo usermod -a -G gpio $USER
# Logout e login
```

### Problema: Motores não se movem

**Verificação:**
1. Confirme pinos em `config.yaml` (usar `gpio readall` para visualizar pinagem).
2. Teste manualmente com `gpiozero`:
```python
from gpiozero import Motor
motor = Motor(forward=17, backward=27)
motor.forward()
```
3. Verifique alimentação da ponte-H (12V).

### Problema: Câmera retorna gradiente cinzento

**Motivo:** Sistema está usando câmera mock (esperado em PC).

**Para RPi:** Confirme câmera conectada com `libcamera-hello --list-cameras`.

---

## Documentação Completa

Consulte a documentação online ou localmente:

```bash
# Compilar documentação localmente
pip install mkdocs-material
mkdocs serve
# Acesse http://localhost:8000
```

**Seções de documentação:**
- [Visão Geral](docs/index.md)
- [Arquitetura](docs/arquitetura.md)
- [API da Classe Rover](docs/api/rover.md)
- [Módulos de Hardware](docs/api/drivers.md)

---

## Deploy de Documentação

A documentação é publicada automaticamente no GitHub Pages quando há mudanças em:
- `docs/**` (diretório de documentação)
- `mkdocs.yml` (configuração)
- `lib_rover/**` (código com docstrings)

**Deploy manual:**
```bash
pip install mkdocs-material mkdocs-glightbox
mkdocs gh-deploy --force
```

---

## Contribuições

Contribuições são bem-vindas. Para reportar bugs ou sugerir features, abra uma issue no repositório.

---

## Licença

Este projeto é licenciado sob [especificar licença - ex.: MIT].

---


## Referências e Recursos

- [Raspberry Pi 5 Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [OpenCV Tutorials](https://docs.opencv.org/)
- [Hough Transform (Wikipedia)](https://en.wikipedia.org/wiki/Hough_transform)