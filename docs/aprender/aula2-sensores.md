# Aula 2: Sensores de distância, ruído e máquinas de estados

Na aula 1, o Rover se movia "de olhos fechados". Agora ele passa a perceber o ambiente com o Lidar TF-Luna. Toda medida real tem ruído e falhas, e um comportamento que reage a cada leitura isolada fica instável. Nesta aula, você caracteriza o sensor, filtra o sinal e organiza o comportamento do robô numa máquina de estados.

## Objetivos

Ao final da aula, você deve ser capaz de:

- ler distância, força do sinal e temperatura do Lidar e reconhecer leituras inválidas;
- comparar média móvel, mediana móvel e filtro exponencial quanto a ruído, outliers e atraso;
- usar **histerese** para evitar que o robô oscile entre dois comportamentos;
- projetar um comportamento reativo como uma **máquina de estados finita** (FSM).

## Conceitos

### O sensor

O TF-Luna mede distância pelo **tempo de voo** de um pulso de luz infravermelha, cerca de 100 vezes por segundo, num único ponto à frente do sensor. Cada leitura traz três valores:

| Valor | Significado |
|---|---|
| distância (cm) | faixa garantida de 20 cm a 8 m |
| força do sinal | intensidade da luz refletida; abaixo de 100 ou saturada (65535), a leitura não é confiável |
| temperatura (°C) | temperatura do chip; o plugin desliga o sensor se ela passar do limite |

`rover.lidar.get_distance()` devolve `None` quando a força do sinal indica uma leitura inválida, e `is_obstacle(limite)` só responde `True` para leituras válidas. Mesmo as leituras válidas têm **ruído** (variações de alguns centímetros) e, ocasionalmente, **outliers**: reflexos em superfícies brilhantes ou escuras que produzem valores absurdos.

### Filtros

Para um sinal $x_k$ (a leitura no instante $k$):

| Filtro | Fórmula | Ruído | Outliers | Atraso |
|---|---|---|---|---|
| Média móvel | $y_k = \frac{1}{n}\sum_{i=0}^{n-1} x_{k-i}$ | reduz | espalha o erro por $n$ amostras | $\approx (n-1)/2$ amostras |
| Mediana móvel | $y_k = \mathrm{mediana}(x_{k-n+1}, \dots, x_k)$ | reduz | **elimina** (se forem menos da metade da janela) | $\approx (n-1)/2$ amostras |
| Exponencial | $y_k = \alpha x_k + (1-\alpha)\, y_{k-1}$ | reduz | espalha o erro | cresce quando $\alpha$ diminui |

Não existe filtro sem custo: quanto mais o sinal é suavizado, mais ele **atrasa** em relação à realidade. Para um robô a 25 cm/s, um atraso de 0,2 s significa 5 cm a mais antes de reagir.

### Histerese

Com um único limite ("obstáculo se $d < 30$ cm"), uma leitura que oscila entre 29 e 31 cm faz o robô alternar entre avançar e girar a cada ciclo. A **histerese** usa dois limites: entra no estado de obstáculo abaixo de 30 cm e só sai acima de 45 cm. Entre os dois, o estado anterior é mantido.

### Máquina de estados finita

Um comportamento reativo pode ser descrito por um conjunto de **estados**, uma **ação** associada a cada estado e **transições** disparadas pelas leituras:

```
               d < 30 cm
   AVANCAR  ─────────────▶  GIRAR
      ▲                       │
      └───────────────────────┘
               d > 45 cm

   leitura inválida (de qualquer estado) ─▶ PARADO
```

Separar a decisão (`decidir(estado, leitura)`) da ação (`agir(estado)`) deixa o comportamento fácil de testar e de estender.

## Prática

Os scripts estão em `tutoriais/aula2_sensores/`. Execute-os a partir da pasta `tutoriais/`.

### 1. Lendo o sensor

```bash
python aula2_sensores/leitura_lidar.py
```

```python
distancia, forca, temperatura = lidar.get_read()   # leitura bruta
valida = lidar.get_distance()                      # None se não for confiável
lidar.is_obstacle(30)                              # True se houver algo a até 30 cm
```

No PC, o Lidar é simulado, e o script usa `set_distance()` para imitar um obstáculo se aproximando. No Rover, aproxime a mão do sensor.

### 2. Comparando filtros

```bash
python aula2_sensores/filtros.py
```

O script gera um sinal sintético: o Rover se aproxima de uma parede de 150 cm a 20 cm, com ruído gaussiano de 2 cm e 5% de leituras espúrias (0 ou 800 cm). Ele aplica os três filtros, mostra o erro de cada um em relação à distância real e salva `aula2_sensores/saida/filtros.png`:

| Sinal | Erro (RMSE) |
|---|---|
| sem filtro | 109,9 cm |
| média móvel ($n=5$) | 49,5 cm |
| mediana móvel ($n=5$) | 1,6 cm |
| exponencial ($\alpha=0{,}3$) | 47,2 cm |

Com outliers, a mediana é muito melhor: a média e o filtro exponencial deixam cada leitura espúria "vazar" para várias amostras seguintes.

### 3. Comportamento reativo

```bash
python aula2_sensores/maquina_estados.py
```

```python
def decidir(estado, distancia):
    if distancia is None:
        return "PARADO"
    if estado in ("AVANCAR", "PARADO") and distancia < LIMITE_PERTO:
        return "GIRAR"
    if estado in ("GIRAR", "PARADO") and distancia > LIMITE_LONGE:
        return "AVANCAR"
    return estado
```

No PC, a classe `MundoSimulado` faz o papel do ambiente: a distância diminui enquanto o Rover avança e, ao girar, aparece um novo caminho. O terminal mostra cada transição:

```
t=  0.0 s  d=120 cm  PARADO -> AVANCAR
t=  3.7 s  d=28 cm  AVANCAR -> GIRAR
t=  4.8 s  d=118 cm  GIRAR -> AVANCAR
```

## Exercícios

⭐ **1. Escolha da janela.** Rode `filtros.py` com janelas de 3, 5, 9 e 15 amostras para a média e a mediana. Monte uma tabela de RMSE. Qual o melhor tamanho? O que acontece com o atraso?

⭐ **2. Filtro exponencial.** Varie $\alpha$ de 0,1 a 0,9. Explique, pela fórmula, por que $\alpha$ pequeno suaviza mais e atrasa mais.

⭐⭐ **3. Mediana na máquina de estados.** Acrescente uma mediana móvel de 5 leituras entre o `get_distance()` e o `decidir()`. Para testar, faça o `MundoSimulado` devolver uma leitura espúria de 5 cm com probabilidade de 10%. Compare o número de transições com e sem o filtro.

⭐⭐ **4. Estado RECUAR.** Se o obstáculo estiver a menos de 15 cm, o Rover deve dar ré por 0,5 s antes de girar. Desenhe o novo diagrama de estados e implemente.

⭐⭐ **5. Sem histerese.** Faça `LIMITE_LONGE = LIMITE_PERTO` e acrescente ao mundo um ruído de ±3 cm. Conte as transições em 15 s e explique o resultado.

⭐⭐⭐ **6. Caracterizando o sensor.** No Rover, posicione um anteparo a 30, 60, 100 e 200 cm e colete 200 leituras em cada distância. Calcule média, desvio padrão e porcentagem de leituras inválidas para cada caso e para superfícies diferentes (papel branco, tecido preto, vidro). O ruído depende da distância? E da superfície?

## No Rover

- O Lidar real é ligado à UART (`/dev/ttyAMA0`); a [Instalação](../instalacao.md) explica como ativá-la.
- Na `maquina_estados.py`, o mundo simulado só é usado no PC: no Rover, a distância vem do sensor real e o robô se move de verdade. Teste primeiro com `ROVER_SIMULATE=1`, que simula só os motores e o Lidar.
- Leituras abaixo de 20 cm não têm precisão garantida: use limites de 20 cm ou mais.

## Para saber mais

- SIEGWART, R.; NOURBAKHSH, I.; SCARAMUZZA, D. *Introduction to Autonomous Mobile Robots*, cap. 4 (sensores e incerteza).
- ARKIN, Ronald C. *Behavior-Based Robotics*. MIT Press, 1998 (arquiteturas reativas).
- Referência da API: [Lidar e Lidar simulado](../api/sensores.md).
