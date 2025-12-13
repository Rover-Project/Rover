# Estudo da função HoughTransform na linguagem Python

## 1. Transformada de Hough
A Transformada de Hough é uma técnica usada em Visão Computacional para encontrar formas geométricas dentro de uma imagem, principalmente:

* Linhas retas

* Círculos

* Elipses

 Esse método - Hough Transform - é fundamental, projetado para detectar formas geométricas (linhas, círculos, elipses) que podem ser descritas por um conjunto de parâmetros conhecidos, mesmo que estas formas estejam incompletas ou obscurecidas por ruídos na imagem.
 
-----
## 2. Como o método funciona?

 2.1 Primeiramente, é realizada a detectação das bordas da imagem (geralmente com Canny).

2.2 Cada ponto da borda "faz votos" para possíveis linhas ou círculos que poderiam passar por ele.

2.3 Esses votos são guardados em um acumulador (como uma tabela de contagem).

2.4 Onde houver mais votos, significa que há uma forma real na imagem.

Ou seja:

A Transformada de Hough transforma o problema de “ver uma linha na imagem” no problema de “ver um pico de votos” no espaço de parâmetros.

---
## 3. Funcionamento da Transformada de Hough no OpenCV
No OpenCV, a Transformada de Hough está disponível em duas principais variantes:

- cv2.HoughLines() – detecção de linhas retas via parametrização polar 
(
𝜌
,
𝜃
).

- cv2.HoughCircles() – detecção de círculos utilizando o algoritmo de Transformada de Hough Gradiente.


### 3.1 Parâmetros de HoughCircles
```bash
circles = cv2.HoughCircles(
    image,
    cv2.HOUGH_GRADIENT,
    dp,
    minDist,
    param1,
    param2,
    minRadius,
    maxRadius
)
```

| Parâmetros        | Tipo          | Função                                  | Impacto
| ------------------|---------------|-----------------------------------------| -----------------------------------|
| image             | numpy.ndarray | Imagem de entrada em tons de cinza      | Obrigatório                        |                        
| cv2.HOUGH_GRADIENT| int           | Método de detecção                      | Usa gradiente para reduzir custo   |
| dp                | double        | Resolução do acumulador                 | Influencia velocidade e precisão   |
| minDist           | double        | Distância mínima entre centros          | Evita duplicações                  |
| param1            | double        | Limiar do Canny interno                 | Controla sensibilidade das bordas  |
| param2            | double        | Votos mínimos no acumulador             | Controla rigor da detecção         |
| minRadius         | int           | Menor raio detectado                    | Filtra ruídos                      |
| maxRadius         | int           | Maior raio detectado                    | Limita tamanho do objeto detectado |








