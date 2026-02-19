# Módulo de Processamento de Imagem - Estrutura Funcional

Este módulo é responsável pelo **pré-processamento de imagens** capturadas pelo Rover, fornecendo ferramentas reutilizáveis para corte de imagem, ajuste de brilho, segmentação por cor e detecção de bordas.

O objetivo é **padronizar e simplificar** operações comuns de visão computacional antes de etapas como detecção, navegação ou tomada de decisão.

---

## 📁 Estrutura

````
processing/
├── __init__.py         # Inicialização do módulo
└── processing_image.py # Ferramentas de pré-processamento de imagem
````

---

## 🔧 Classe Principal

### ProcessingImage (`processing_image.py`)
Classe utilitária com métodos de classe (`@classmethod`) para processamento de imagens usando **OpenCV** e **NumPy**.

Não mantém estado interno — todos os métodos recebem e retornam imagens (`numpy array`).

---

## 🧩 Funcionalidades

### 1. Corte de Imagem (ROI)

Corta um frame em uma **região de interesse** definida pelo usuário.

**Uso:**
```python
from rover_lib.modules.processing.processing_image import ProcessingImage

roi = (100, 50, 300, 200)  # x_start, y_start, width, height
cropped = ProcessingImage.cutImage(frame, roi)
```
---

### 2. Ajuste de Brilho (Correção Gamma)

Realiza ajuste de brilho usando correção gamma.

* gamma > 1: escurece a imagem

* gamma < 1: clareia a imagem

**Uso:**
```python
adjusted = ProcessingImage.ligh_adjustment(frame, gamma=1.8)
```

---

### 3. Segmentação por Cor (HSV)

Aplica segmentação de cor utilizando o espaço HSV. Por padrão, o método está configurado para segmentação da cor vermelha, usando dois intervalos HSV para lidar com a circularidade do canal Hue.

**Uso:**
```python
mask = ProcessingImage.color_segmentation(frame)
```
Também é possível customizar os intervalos de cor:
```python
mask = ProcessingImage.color_segmentation(
    frame,
    low_color1=(35, 100, 100),
    upper_color1=(85, 255, 255)
)
```
---

### 4. Segmentação Dupla por Cor

Executa uma segmentação dupla, combinando:

* Segmentação em imagem normal

* Segmentação em imagem escurecida (gamma ajustado)

Essa abordagem melhora a detecção em condições de iluminação adversas.

**Uso:**
```python
mask = ProcessingImage.color_dual_segmentation(frame)
```
---

### 5. Detecção de Bordas

Aplica o filtro de bordas Canny.

**Uso:**
```python
edges = ProcessingImage.edge_filter(frame, theres1=50, theres2=150)
```
---

## 🔄 Compatibilidade

Este módulo é independente de hardware e pode ser executado:

* No computador local (Linux, Windows, WSL)

* Na Raspberry Pi

---

## 🧪 Dependências

Este módulo depende das seguintes bibliotecas:

* opencv-python

* numpy

Instalação:
```bash
pip install opencv-python numpy
```



