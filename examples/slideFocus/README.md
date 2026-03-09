# SlideFocus
Sistema de ajuste de forma manual utilizando o teclado.

# Estrutura 
```bash
slideFocus/
│
├── config.yaml
├── main.py
└── README.md
```

## config.yaml
Arquivo de configuração da câmera. Facilidando a manipulação dos parâmetros sem necessidade de alteração diretamente no código.

```Yaml
camera:
  fps: 30
  resolution:
    h: 4656
    w: 3496
  brigh: 0 # Brilho
  contrast: 1 # Contraste 
  saturation: 1 # Saturação
```
Esse arquivo define:
- resolução da câmera
- taxa de frames
- brilho
- contraste
- saturação

# Dependências 
Principais dependências utilizadas:
- Python

Além disso o projeto depende da biblioteca do projeto:
```bash
roverlib
```
que fornece:
- interface de câmera
- processamento de imagem
- módulos de visão computacional

# Como usar 
o processo de utilização é simples. Dentro da pasta `examples`:

```bash
python -m slideFocus.main
```
Explicação:
- ``python``: Roda o programa utilizando o python padrão da máquina ou do virtual env.
- ``-m``: Parâmetro que informa que o programa deve ser executado como um môdulo python.
- ``slideFocus.main``: caminho até o aquivo de execução.

# Manipulção do foco 
Teclas de aceitas:

- Tecla `w`: Aumenta o foco, aproximando do objeto de interesse.
- Tecla `s`: Diminui o foco, distânciando do objeto de interesse.
- Tecla `q`: Usada para sair do programa.