# Aula 3: Imagem digital e espaços de cor

A câmera é o sensor mais rico do Rover, mas para o programa uma imagem é só uma matriz de números. Nesta aula, você manipula essa matriz, entende por que o espaço de cor HSV é mais adequado que o BGR para encontrar objetos coloridos e mede a qualidade de uma segmentação com um critério numérico.

## Objetivos

Ao final da aula, você deve ser capaz de:

- acessar e interpretar pixels de uma imagem como array NumPy;
- converter entre BGR, RGB e HSV e explicar o que cada canal representa;
- segmentar um objeto por cor com limiares e limpar a máscara com morfologia;
- avaliar uma segmentação com o IoU e comparar métodos sob iluminação variável.

## Conceitos

### A imagem como matriz

Um frame da câmera do Rover é um array NumPy de forma `(altura, largura, 3)` e tipo `uint8` (valores de 0 a 255). O pixel na coluna $x$ e linha $y$ é `img[y, x]`, um vetor com os três canais de cor. **A linha vem primeiro**: é a convenção de matrizes, oposta à de coordenadas $(x, y)$.

A RoverLib entrega os frames em **BGR** (azul, verde, vermelho), a ordem do OpenCV. Para outras bibliotecas (MediaPipe, Matplotlib, PIL), que usam **RGB**, peça a conversão com `camera.set_format("rgb")` ou `format: rgb` no `config.yaml`.

### Por que HSV

Em BGR, a cor e a iluminação estão misturadas nos três canais: um objeto vermelho na sombra tem valores de R, G e B todos menores. Um limiar como "R > 150" funciona com boa luz e falha na sombra.

O espaço **HSV** separa essas informações:

| Canal | Significado | Faixa no OpenCV |
|---|---|---|
| H (matiz) | qual é a cor, como um ângulo no círculo cromático | 0–179 (graus ÷ 2) |
| S (saturação) | quão "pura" é a cor; 0 é cinza | 0–255 |
| V (valor) | brilho | 0–255 |

A matiz de um objeto muda pouco com a iluminação, então um limiar em H é mais robusto. O vermelho tem uma particularidade: fica nas **duas pontas** da escala de matiz (perto de 0 e de 179), por isso é segmentado com dois intervalos.

### Segmentação, morfologia e avaliação

A **limiarização** (`cv2.inRange`) produz uma máscara binária: 255 onde o pixel está na faixa de cor, 0 no resto. Ruído na imagem gera pontos isolados e buracos, que a **morfologia matemática** corrige:

- **abertura** (erosão seguida de dilatação): remove pontos menores que o elemento estruturante;
- **fechamento** (dilatação seguida de erosão): preenche buracos e emendas.

Para comparar métodos, é preciso um critério numérico. O **IoU** (*intersection over union*) compara a máscara obtida $A$ com a máscara verdadeira $B$:

$$
\mathrm{IoU} = \frac{|A \cap B|}{|A \cup B|}
$$

O IoU vale 1 para uma segmentação perfeita e 0 quando não há sobreposição. Ele é a mesma métrica usada para avaliar detectores de objetos e redes de segmentação.

## Prática

Os scripts estão em `tutoriais/aula3_imagem/`. Eles usam **cenas sintéticas** (módulo `tutoriais/cena.py`): imagens geradas por código em que a posição, o tamanho e a cor de cada objeto são conhecidos. Assim, os algoritmos podem ser testados sem câmera e comparados com a "verdade".

### 1. A imagem como matriz

```bash
python aula3_imagem/imagem_como_matriz.py
```

```
forma: (480, 640, 3)  (altura, largura, canais)   tipo: uint8
pixel (220, 260) em BGR: B=39 G=19 R=201
o mesmo pixel em HSV: H=177 (matiz, 0-179)  S=231 (saturação)  V=201 (brilho)
```

O script salva a cena e um mosaico com os canais B, G, R, H, S e V em `aula3_imagem/saida/`. Observe no mosaico que o canal H destaca os objetos pela cor, independentemente do gradiente de luz do fundo.

### 2. BGR x HSV sob iluminação variável

```bash
python aula3_imagem/segmentacao.py
```

O script segmenta o círculo vermelho com quatro métodos e calcula o IoU de cada um, escurecendo a cena progressivamente:

| Brilho | BGR | HSV | HSV + morfologia | RoverLib |
|---|---|---|---|---|
| 0,4 | 0,00 | 0,72 | 0,84 | 0,01 |
| 0,6 | 0,00 | 0,94 | 0,99 | 0,99 |
| 0,8 | 0,78 | 0,99 | 1,00 | 1,00 |
| 1,0 | 1,00 | 1,00 | 1,00 | 1,00 |

- O limiar em **BGR** falha assim que a cena escurece.
- O limiar em **HSV** continua funcionando, e a morfologia melhora o resultado.
- A função `ProcessingImage.color_segmentation()` da RoverLib exige brilho mínimo (V ≥ 70) e falha na cena mais escura: é uma escolha de projeto para ignorar regiões escuras demais, onde a matiz não é confiável.

### 3. Ajustando limiares com a câmera

```bash
python aula3_imagem/ajuste_hsv.py
```

Com uma webcam (ou no Rover), o script mostra a máscara ao vivo e controles deslizantes para os seis limites HSV. Use-o para descobrir a faixa de cor de um objeto real. Ele pede os frames diretamente em HSV com `camera.set_format("hsv")`.

## Exercícios

⭐ **1. Outras cores.** Altere `segmentar_hsv()` para segmentar o círculo azul e o quadrado verde da cena. Qual a faixa de matiz de cada um? *(Dica: imprima `hsv[y, x]` no centro de cada objeto.)*

⭐ **2. Elemento estruturante.** Varie o tamanho do kernel da morfologia (3, 5, 9, 15) com brilho 0,4. O IoU sempre melhora? O que acontece com as bordas do objeto?

⭐⭐ **3. Robustez ao ruído.** Fixe o brilho em 1,0 e varie o ruído de 0 a 40. Faça um gráfico do IoU de cada método em função do ruído.

⭐⭐ **4. Equalização.** Antes de segmentar a cena com brilho 0,4, aplique `cv2.equalizeHist` no canal V (ou o CLAHE, `cv2.createCLAHE`). O IoU do limiar em BGR melhora? E o do HSV?

⭐⭐⭐ **5. Faixa ótima.** Escreva uma busca que encontre automaticamente os limites de S e V que maximizam o IoU médio do círculo vermelho para brilhos de 0,4 a 1,2. Discuta o risco de "sobreajustar" a faixa a essas cenas.

⭐⭐⭐ **6. Cena real.** Com o `ajuste_hsv.py`, encontre a faixa de um objeto real sob a luz da sala e sob a luz de uma janela. As faixas coincidem? Proponha uma estratégia para a segmentação funcionar nas duas condições.

## No Rover

- A câmera do Rover (Arducam IMX519) tem foco automático; para objetos próximos, use a `AfCamera` ou o exemplo `continuousFocus`.
- O ajuste `brightness` da câmera soma um valor fixo a cada pixel: valores pequenos (±0,1) já mudam bastante a segmentação.
- Os frames chegam em BGR: confira com um objeto vermelho, que deve aparecer branco na máscara.

## Para saber mais

- SZELISKI, R. *Computer Vision: Algorithms and Applications*, 2. ed., cap. 2 (formação da imagem e cor) e cap. 3 (processamento de imagens, morfologia).
- GONZALEZ, Rafael C.; WOODS, Richard E. *Processamento Digital de Imagens*. 3. ed. Pearson, 2010, caps. 6 (cor) e 9 (morfologia).
- Referência da API: [`ProcessingImage`](../api/visao.md) e [`Camera.set_format`](../api/camera.md).
