# RoverKeypadControl
Um controle para o Rover via teclado, possibilitando também uma vizualização de frames se da câmera se estiver disponivel.

# Estrutura 
```bash
roverKeypadControl/
│
├── config.yaml
├── main.py
└── README.md
```

## config.yaml
Arquivo de configuração do hardware. Facilidando a manipulação dos parâmetros sem necessidade de alteração diretamente no código.

```Yaml
camera:
  fps: 30
  resolution:
    h: 4656
    w: 3496
  brigh: 0 # Brilho
  contrast: 1 # Contraste 
  saturation: 1 # Saturação

motor:
  right: [15, 16]
  left: [12, 11]
  calibration:
    left: 1
    right: 1
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
Principais dependências utilizadas:
- Python
- openCV
- numpy

Além disso o projeto depende da biblioteca do projeto:
```bash
roverlib
```
que fornece:
- interface de câmera
- processamento de imagem
- Controle dos motores
- módulos de visão computacional

# Como usar 
o processo de utilização é simples. Dentro da pasta `examples`:

```bash
python -m roverKeypadControl.main
```
Explicação:
- ``python``: Roda o programa utilizando o python padrão da máquina ou do virtual env.
- ``-m``: Parâmetro que informa que o programa deve ser executado como um môdulo python.
- ``roverKeypadControl.main``: caminho até o aquivo de execução.

# Manipulção do Rover por meio do teclado
Teclas de aceitas:

- Tecla `w`: Move para frente.
- Tecla `s`: Move para trás.
- Tecla `a`: Gira para a esquerda.
- Tecla `d`: Gira para a direita.
- Tecla `q`: Usada para sair do programa.