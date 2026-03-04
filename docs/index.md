# Bem-vindo à RoverLib

A **RoverLib** é uma biblioteca modular em Python para **Raspberry Pi 5**, projetada especificamente para viabilizar arquiteturas de robótica. A plataforma abstrai a complexidade de drivers de hardware em uma API de alto nível altamente coesa e compreensível, ideal para rápida prototipagem e desenvolvimento de comportamentos complexos.

## Conceito Fundamental

A **RoverLib** foca em uma abordagem modular, onde os desenvolvedores podem compor instâncias que lidam de forma transparente com os hardwares de baixo nível (Câmera, Motores, GPIO) através de comandos simples e limpos. Isto reduz a necessidade de expertise em programação de sistemas embarcados para focar no fluxo do processo.

### Exemplo de Fluxo Operacional

**Descrição de Movimento Básico:**

**Código Python executável:**

```python
from roverlib.modules.movement.robot import Robot
import time

def main():
    # Inicializa componentes de hardware (usa mocks virtuais no PC)
    rover = Robot(left=(17, 27), right=(22, 23))

    # Executa movimento com duração temporal
    rover.forward(speed=50, duration=2.0)

    # Libera recursos
    rover.cleanup()

if __name__ == "__main__":
    main()
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
# Instala diretamente do PyPI (ambiente virtual recomendado)
pip install roverlib[cli]

# Cria um novo projeto via CLI
rover new meu_projeto
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

