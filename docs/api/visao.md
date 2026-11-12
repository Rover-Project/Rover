# Visão e processamento de imagem

Funções que recebem um frame (array NumPy em BGR) e devolvem o resultado do processamento. Funcionam com qualquer câmera, inclusive a webcam do PC.

```python
from roverlib import ProcessingImage, VisionModule

mascara = ProcessingImage.color_segmentation(frame)       # vermelho por padrão
circulo, bordas = VisionModule.houghCircleDetect(mascara)  # (x, y, raio) ou None
```

::: roverlib.modules.processing.processing_image.ProcessingImage

::: roverlib.modules.vision.visionModule.VisionModule
