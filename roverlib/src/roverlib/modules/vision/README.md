# Módulo de Visão - Estrutura Funcional

O módulo de visão é responsável por **interpretar imagens capturadas pela câmera do Rover** e extrair informações relevantes para navegação e tomada de decisão.

Ele utiliza técnicas de **visão computacional clássica com OpenCV**, integrando diretamente com o módulo de processamento de imagem.

---

## 📁 Estrutura

````
vision/
├── init.py         # Inicialização do módulo
└── visionModule.py # Implementação principal do sistema de visão
````
---

## 🔧 Classe Principal

### VisionModule (`visionModule.py`)

Classe responsável por **processar frames da câmera** e gerar informações como:

- desvio da linha para navegação
- detecção de obstáculos
- detecção de círculos (alvos, sinais, etc.)

---

## 🚀 Inicialização

```python
from rover_lib.modules.vision.visionModule import VisionModule

vision = VisionModule(resolution=(640, 480))
```

## 🧩 Funcionalidades
### 1. Detecção de Círculos — Transformada de Hough

Detecta círculos na imagem usando HoughCircles com pré-processamento de bordas.

**Uso:**
```python
circle, edges = VisionModule.houghCircleDetect(frame)

if circle:
    x, y, r = circle
```
**Retorna:**

* Informações como: (x, y, raio) do maior círculo detectado

* Imagem de bordas processada

---

### 2. Detecção de Círculos via Contorno (Canny + Circularidade)

Alternativa à Hough, baseada em:

* Detecção de contornos

* Cálculo de circularidade

**Uso:**
```python
circle = VisionModule.circleCannyDetect(frame)
```
---

### 3. Seguimento de Linha (Line Following)

Processa o frame para detectar uma linha e calcular o desvio do centro. Esse valor pode ser usado diretamente pelo módulo de movimento para controle de direção.

**Uso:**
```python
desvio, frame_debug = vision.process_frame_for_line_following(frame)
```
**Retorno:**

* desvio: valor entre -1.0 (esquerda) e 1.0 (direita)

* frame_processado: imagem com marcações visuais

---

### 4. Detecção de Obstáculos

Detecta objetos à frente do rover com base em:

* Cor (HSV)

* Área mínima

Por padrão, detecta objetos vermelhos (ex: bolas, balões).

**Uso:**
```python
obstacle, frame_debug = vision.detect_obstacle(frame)
```
**Com cor personalizada:**
```python
lower = (35, 100, 100)
upper = (85, 255, 255)

obstacle, _ = vision.detect_obstacle(frame, color_range=(lower, upper))
```

---

## 🔗 Integração com o módulo de processamento

O módulo de visão utiliza diretamente:
```python
from rover_lib.modules.processing.processing_image import ProcessingImage
```

Funções utilizadas:

* edge_filter

* color_segmentation

---

## 🧪 Dependências

Este módulo depende de:

* opencv-python

* numpy

Instalação:
```bash
pip install opencv-python numpy
```
