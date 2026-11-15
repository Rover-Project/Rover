# Aula 4: Detecção de objetos por cor e forma

A segmentação da aula 3 diz *quais pixels* têm a cor procurada. Para o robô agir, é preciso transformar esses pixels em informação geométrica: onde está o objeto, qual o seu tamanho, que forma ele tem. Nesta aula, você extrai essas grandezas, compara dois detectores de círculos e aprende a avaliar um algoritmo de visão com um experimento controlado.

## Objetivos

Ao final da aula, você deve ser capaz de:

- extrair contornos de uma máscara e calcular área, perímetro e centroide pelos momentos;
- classificar formas pela circularidade;
- explicar o funcionamento da Transformada de Hough para círculos;
- planejar e executar uma avaliação quantitativa de detectores (taxa de acerto e erro).

## Conceitos

### Contornos e momentos

Um **contorno** é a sequência de pixels na fronteira de uma região da máscara (`cv2.findContours`). Os **momentos** da região resumem sua geometria:

$$
M_{pq} = \sum_x \sum_y x^p\, y^q\, I(x, y)
$$

Para uma máscara binária, $M_{00}$ é a **área** e o **centroide** é

$$
\bar{x} = \frac{M_{10}}{M_{00}} \qquad \bar{y} = \frac{M_{01}}{M_{00}}
$$

O centroide é a grandeza mais usada para controlar o robô: o erro horizontal $\bar{x} - \frac{\text{largura}}{2}$ diz para que lado girar (aula 5).

### Circularidade

A **circularidade** compara a área $A$ com o perímetro $P$:

$$
C = \frac{4\pi A}{P^2}
$$

Ela vale 1 para o círculo perfeito, $\pi/4 \approx 0{,}785$ para o quadrado e diminui para formas alongadas ou irregulares. Em imagens digitais, o perímetro medido em pixels é maior que o real (a borda é uma "escada"), então um círculo dá cerca de 0,9.

### Transformada de Hough para círculos

Cada pixel de borda "vota" em todos os círculos que poderiam passar por ele. Os votos são acumulados num espaço de parâmetros $(x_c, y_c, r)$, e os picos desse acumulador são os círculos mais prováveis. Na prática, o OpenCV usa o gradiente da borda para votar só na direção da normal, o que torna o cálculo viável.

| | Hough | Contorno + circularidade |
|---|---|---|
| Ideia | votação no espaço de parâmetros | geometria de uma região fechada |
| Funciona com objeto parcialmente encoberto | sim | não (a região deixa de ser redonda) |
| Sensível a bordas fragmentadas por ruído | pouco | muito |
| Precisão quando a máscara é limpa | boa | excelente |

A RoverLib oferece os dois: `VisionModule.houghCircleDetect()` e `VisionModule.circleCannyDetect()`. Os exemplos `circleDetect` e `folowCircle` combinam ambos por votação.

### Avaliando um detector

Testar um detector "olhando se funcionou" em algumas imagens não permite comparar métodos nem saber em que condições ele falha. Uma avaliação quantitativa precisa de:

1. **dados com verdade conhecida**, aqui obtidos por cenas sintéticas;
2. um **critério de acerto**, como centro a menos de 10 px e raio com erro menor que 20%;
3. **métricas**: taxa de acerto e erro médio entre os acertos;
4. **condições variadas** (ruído, iluminação), sempre com as **mesmas cenas** para todos os métodos.

## Prática

Os scripts estão em `tutoriais/aula4_deteccao/`.

### 1. Formas pela circularidade

```bash
python aula4_deteccao/formas.py
```

```python
m = cv2.moments(contorno)
area = m["m00"]
cx, cy = m["m10"] / area, m["m01"] / area
circularidade = 4 * math.pi * area / cv2.arcLength(contorno, True) ** 2
```

```
   centroide     área  perímetro  circularidade  forma
(  480, 360)     8094      357.7          0.795  quadrado
(  220, 260)    11118      394.0          0.900  círculo
(  470, 150)     4910      262.1          0.898  círculo
(  110, 110)     4894      277.7          0.798  quadrado
```

Os centroides coincidem com os centros verdadeiros dos objetos, e o limiar de 0,85 separa as formas. A imagem anotada fica em `aula4_deteccao/saida/formas.png`.

### 2. Comparando os detectores da RoverLib

```bash
python aula4_deteccao/comparar_detectores.py
```

Para cada condição, o script gera 40 cenas com uma bola vermelha de posição e raio aleatórios (15 a 110 px) e dois objetos de outras cores, segmenta com `color_dual_segmentation()` e aplica os dois detectores:

| Condição | Detector | Acertos | Erro do centro | Erro do raio |
|---|---|---|---|---|
| boa iluminação | Hough | 92% | 1,5 px | 1,7% |
| boa iluminação | Contorno | 90% | 0,0 px | 0,0% |
| ruído forte | Hough | 48% | 4,4 px | 3,1% |
| ruído forte | Contorno | 10% | 0,9 px | 0,4% |
| cena escura | Hough | 92% | 1,5 px | 1,9% |
| cena escura | Contorno | 90% | 0,1 px | 0,0% |

Com a máscara limpa, o contorno é mais preciso; com ruído forte, ele quase deixa de funcionar, enquanto o Hough degrada aos poucos. É por isso que os exemplos combinam os dois.

### 3. Ao vivo

```bash
python aula4_deteccao/camera_ao_vivo.py
```

Com uma webcam ou no Rover, mostre uma bola ou tampa **vermelha** à câmera. O círculo verde é o do Hough e o azul, o do contorno.

## Exercícios

⭐ **1. Quadrado ou círculo?** Acrescente à cena um triângulo (`cv2.fillPoly`) e calcule a circularidade. Que valor teórico você espera? Ajuste a classificação para três formas.

⭐ **2. Polígonos.** Use `cv2.approxPolyDP` para contar os vértices de cada contorno e classificar as formas por esse critério. Compare com a circularidade.

⭐⭐ **3. Onde o contorno erra?** Em `comparar_detectores.py`, salve as cenas em que o detector de contorno falha com boa iluminação. O que elas têm em comum? *(Dica: observe a posição da bola em relação aos outros objetos e às bordas da imagem.)*

⭐⭐ **4. Suavização.** Aplique um filtro gaussiano (`cv2.GaussianBlur`) na imagem antes da segmentação e repita a avaliação com ruído forte. Qual detector se beneficia mais?

⭐⭐ **5. Falsos positivos.** Acrescente cenas **sem** a bola vermelha (só os objetos de distração) e conte quantas vezes cada detector "encontra" um círculo mesmo assim. Calcule precisão e revocação.

⭐⭐⭐ **6. Votação.** Implemente uma combinação dos dois detectores (por exemplo, usar o contorno quando os dois concordam e o Hough nos outros casos) e mostre, com a avaliação, se ela supera os dois isoladamente em todas as condições.

## No Rover

- Use um objeto vermelho e fosco; superfícies brilhantes criam reflexos brancos que viram buracos na máscara.
- Objetos muito próximos ficam desfocados: a câmera do Rover tem autofoco (veja o exemplo `continuousFocus`).
- O tamanho aparente (raio em pixels) diminui com a distância: ele serve para estimar a distância ao objeto, como faz o exemplo `folowCircle`.

## Para saber mais

- SZELISKI, R. *Computer Vision: Algorithms and Applications*, 2. ed., cap. 7 (detecção de características, transformada de Hough).
- DUDA, Richard O.; HART, Peter E. Use of the Hough transformation to detect lines and curves in pictures. *Communications of the ACM*, v. 15, n. 1, 1972.
- Referência da API: [`VisionModule`](../api/visao.md).
