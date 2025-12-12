# ML Object Detection - Detecção com Machine Learning

Script simples e portável para detecção de objetos com suporte a múltiplos modelos.

## Arquivos

- **MLModelConfig.py** - Classe unificada para detecção (YOLO, TensorFlow Lite)
- **test_models.py** - Script de teste simples
- **models/** - Diretório para os modelos

## Instalação

```bash
# YOLO
pip install ultralytics opencv-python

# TensorFlow Lite
pip install tflite-runtime opencv-python
```

## Uso

```bash
# Com YOLO
python test_models.py models/best.pt yolo

# Com TensorFlow Lite
python test_models.py models/model.tflite tflite

# Auto-detectar (pela extensão)
python test_models.py models/model.tflite
```

## Caminho dos Modelos

O script procura modelos em:
1. Caminho absoluto ou relativo fornecido
2. `./models/` 
3. `../../../models/`

## Uso em Código

```python
from MLModelConfig import MLModelConfig

# Carrega modelo
detector = MLModelConfig('models/best.pt')

# Detecta em um frame
detections = detector.detect(frame)

# Ou executa em tempo real
detector.run()
```

## Modelos Suportados

- **YOLO** (.pt, .onnx)
- **TensorFlow Lite** (.tflite)

## Configuração

Antes de executar, personalize em `MLModelConfig.__init__()`:

```python
self.confidence = 0.65    # Confiança mínima
self.min_width = 20       # Largura mínima (pixels)
self.max_width = 30000    # Largura máxima (pixels)
self.frame_skip = 1       # Processar cada N frames
```
