# FolowCircle

Sistema que usa os frames capturados pela câmera para detectar e seguir uma bola vermelha. Usa o sistema base de detecção do examplo **CircleDetect**.

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
  fps: 30
  brigh: 0.25
  saturation: 1
  contrast: 1

motor:
  right: [15, 16] # in3, in4
  left: [12, 11] # in1, in2
  calibration:
    right: 1
    left: 1
```
Esse arquivo define:
- ``camera`` 
    - **resolution**: resolução da câmera
    - **fps**: taxa de frames
    - **brigh**: brilho dos frames
    - **contrast**: contraste dos frames
    - **saturation**: saturação dos frames
- ``motor``
    - **right**: pinos de sinal do motor direito 
    - **left**: pinos de sinal do motor esquerdo
    - ``calibration``
        - **right**: calibração para o motor direito
        - **left**: calibração para o motor esquerdo

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
        ↓
Controlador PID
        ↓
Ativação do motores 
```

# Como usar 
o processo de utilização é simples. Dentro da pasta `examples`:

```bash
python -m folowCircle.main
```
Explicação:
- ``python``: Roda o programa utilizando o python padrão da máquina ou do virtual env.
- ``-m``: Parâmetro que informa que o programa deve ser executado como um môdulo python.
- ``folowCircle.main``: caminho até o aquivo de execução.
- ``camera``: parâmetro opcional que informa que tipo de camera deve usar dentre: webcam, camera, autofocus. Quando o parâmetro não é informado ele roda como a webcam.