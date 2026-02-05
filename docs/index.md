# Bem-vindo à RoverLib

A **RoverLib** é uma biblioteca modular em Python para **Raspberry Pi 5**, projetada especificamente para viabilizar arquiteturas de robótica. A plataforma abstrai a complexidade de drivers de hardware em uma API de alto nível compreensível para Large Language Models (LLMs), permitindo orquestração automática de tarefas robóticas em linguagem natural.

## Conceito Fundamental

Em arquiteturas tradicionais de robótica, a especificação do movimento é estruturada como um conjunto de instruções imperativas. Diferentemente, a abordagem **Code as Policies** permite que um operador humano defina o objetivo em linguagem natural, enquanto um LLM gera o código Python executável que coordena os módulos da plataforma. Isto reduz a necessidade de expertise em programação de sistemas embarcados.

### Exemplo de Fluxo Operacional

**Descrição de tarefa (usuário):**

> Ande para frente por 2 segundos e depois procure por uma bola vermelha. Se encontrar, me avise.

**Código gerado e executado (sistema):**

```python
from rover_lib import Rover

# Inicializa componentes de hardware
rover = Rover()

# Executa movimento com duração temporal
rover.movement.forward(speed=50, duration=2.0)

# Captura frame da câmera
frame = rover.camera.get_frame()

# Processa visão para detecção de objetos circulares
circle = rover.vision.detect_circle(frame, color_range='red')

if circle:
    print(f"Objeto detectado nas coordenadas: {circle}")

# Libera recursos
rover.stop_and_cleanup()
```

---

## Características Técnicas Principais

- **Arquitetura em Camadas:** Separação clara entre camada de drivers (hardware), lógica de comportamento (robot) e inteligência (visão computacional e decisão de LLM).

- **Visão Computacional Híbrida:** Algoritmos clássicos otimizados (Transformada de Hough, detecção de arestas Canny, processamento HSV) operando a 30 FPS na unidade central da RPi 5.

- **Loop de Controle de Tempo Real:** Ciclo de amostragem de 10 ms para tarefas críticas como *Line Following*, permitindo resposta rápida a obstáculos e desvios de trajetória.

- **Compatibilidade Multiplataforma:** Fallback automático para câmera mock em plataformas sem `picamera2`, facilitando desenvolvimento e testes em PC.

- **Modularidade:** Componentes desacoplados permitem integração seletiva de subsistemas (movimento, câmera, visão) conforme necessidade.

---

## Instalação Rápida

```bash
git clone https://github.com/Rover-Project/Rover.git
cd Rover
pip install -r requirements.txt
```

Para configuração avançada em Raspberry Pi (habilitação de câmera, ajustes GPIO), consulte [Instalação Detalhada](instalacao.md).

---

## Tutoriais e Exemplos Funcionais

### 1. Detecção de Círculos com Transformada de Hough

O exemplo `circleDetect` demonstra aplicação de algoritmos de visão computacional clássica para localização de objetos circulares em tempo real. O sistema utiliza suavização Gaussiana, filtro de arestas Canny e Transformada de Hough circular.

**Execução:**

```bash
cd Rover/examples/circleDetect
python main.py
```

**Requisitos:** Câmera conectada (RPi 5) ou webcam integrada (PC). O sistema detecta automaticamente o tipo de câmera disponível e faz fallback se necessário.

**Saída esperada:** Exibição em tempo real de frames processados com círculos detectados marcados (centro, raio). A terminal imprime coordenadas e raios dos círculos localizados.

**Parâmetros de interesse:** O algoritmo de Hough aceita ajustes de sensibilidade (raio mínimo/máximo, distância entre centros) para otimização conforme cena.

---

### 2. Interface Gráfica para Controle Manual de Motores

O módulo `roverTkControl` oferece interface gráfica (Tkinter) para testes de hardware, permitindo controle bidirecional de motores, ajuste fino de velocidade e validação de ponte-H (L298N).

**Execução:**

```bash
cd Rover/examples/roverTkControl
python main.py
```

**Funcionalidade:** Botões de direção (frente, trás, esquerda, direita), slider de velocidade (0–100), e visualização de estado atual. Ideal para validação de calibração de motores antes de execução de algoritmos autônomos.

**Notas operacionais:** Garanta que os pinos GPIO sejam configurados corretamente em `configs/config.yaml` antes de execução.

---

### 3. Detecção de Obstáculos em Tempo Real

Script em `scripts_tests/object_detection/HoughTransform/realTime/grayScale.py` implementa detecção contínua de círculos com visualização OpenCV interativa.

**Execução:**

```bash
python Rover/scripts_tests/object_detection/HoughTransform/realTime/grayScale.py
```

**Parâmetros padrão:**
- `h=680`, `w=480`: Dimensões de captura
- `minDist=40`: Distância mínima entre centros de círculos
- `minRadius=10`, `maxRadius=120`: Limites de raio de detecção

**Controle:** Pressione `q` para encerrar a execução.

---

## Estrutura de Módulos

A plataforma organiza-se em três camadas funcionais:

1. **Drivers de Hardware:** Abstrações para motores DC, câmera (Picamera2), sensores de distância.
2. **Lógica Comportamental (Classe Robot):** Movimentos de alto nível (avançar, recuar, girar), line-following.
3. **Inteligência (Visão Computacional):** Processamento de imagem, detecção de formas, análise ambiental.

Consulte [Arquitetura Detalhada](arquitetura.md) para diagramas de fluxo de dados e integração de componentes.

---

## Documentação Específica

- [Instalação e Configuração de Ambiente](instalacao.md) — Passos para Raspberry Pi e desenvolvimento em PC.
- [Arquitetura de Sistema](arquitetura.md) — Diagramas, fluxos de dados, decisões de design.
- [API da Classe Rover](api/rover.md) — Referência completa de métodos, parâmetros e comportamentos.
- [Módulos de Hardware](api/drivers.md) — Documentação de Robot, CameraModule, VisionModule.
- [Exemplos de Uso](exemplos.md) — Tutoriais passo-a-passo para tarefas comuns.

---

## Publicação de Documentação

Esta documentação é gerada automaticamente via `mkdocs` quando há mudanças em `docs/`, `mkdocs.yml` ou código em `roverLib/`. Consulte [Deploy de Documentação](deploy.md) para instruções de publicação manual.

---

## Suporte e Contribuições

Para relatar problemas, sugestões ou contribuições, acesse o repositório do projeto no GitHub.

