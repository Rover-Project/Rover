# CircleDetect

Sistema de detecção robusta de círculos em tempo real usando visão computacional.
O projeto utiliza segmentação por cor, Transformada de Hough, detecção por contornos (Canny) e um método de votação para melhorar a confiabilidade da detecção.

A detecção é suavizada ao longo do tempo utilizando um histórico da posição do círculo, reduzindo ruídos entre frames.

# Estrutura 
```bash
circleDetect/
│
├── config.yaml
├── main.py
├── README.md
│
└── src/
   └── circleDetect.py

```

## config.yaml
Arquivo de configuração da câmera. Facilidando a manipulação dos parâmetros sem necessidade de alteração diretamente no código.

```Yaml
camera:
  resolution:
    h: 640
    w: 640
  fps: 30
  brigh: 0.25
  contrast: 1
  saturation: 1
```
Esse arquivo define:
- resolução da câmera
- taxa de frames
- brilho
- contraste
- saturação

# Dependências 
Principais bibliotecas utilizadas:
- Python 3.10+
- OpenCV
- NumPy

Além disso o projeto depende da biblioteca do projeto:
```bash
roverlib
```
que fornece:
- interface de câmera
- processamento de imagem
- módulos de visão computacional

# Fluxo Geral do sistema 
O fluxo principal da aplicação é:
```bash
Captura do frame
        ↓
Segmentação por cor
        ↓
Detecção de círculo (Hough)
        ↓
Detecção de círculo (Contorno/Canny)
        ↓
Votação entre métodos
        ↓
Suavização temporal
        ↓
Desenho da detecção no frame
```

# Como usar 
o processo de utilização é simples. Dentro da pasta `examples`:

```bash
python -m circleDetect.main camera
```
Explicação:
- ``python``: Roda o programa utilizando o python padrão da máquina ou do virtual env.
- ``-m``: Parâmetro que informa que o programa deve ser executado como um môdulo python.
- ``circleDetect.main``: caminho até o aquivo de execução.
- ``camera``: parâmetro opcional que informa que tipo de camera deve usar dentre: webcam, camera, autofocus. Quando o parâmetro não é informado ele roda como a webcam.