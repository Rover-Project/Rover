# Aula 1: Locomoção diferencial e malha aberta

O Rover se move como um tanque: não tem volante, e muda de direção girando as rodas de cada lado em velocidades diferentes. Nesta aula, você descreve esse movimento com um modelo matemático, prevê trajetórias no computador e descobre por que comandar o robô "por tempo" acumula erros.

## Objetivos

Ao final da aula, você deve ser capaz de:

- comandar o Rover com `forward()`, `turn_right()`, `move()` e `turn_degrees()`;
- relacionar a velocidade de cada roda com a velocidade linear e angular do robô;
- prever a trajetória de uma sequência de comandos integrando o modelo cinemático;
- explicar por que o controle em **malha aberta** acumula erro e como a calibração o reduz.

## Conceitos

### Robô de acionamento diferencial

Cada lado do Rover tem um motor DC. Chamando de $v_R$ e $v_L$ as velocidades lineares das rodas direita e esquerda e de $L$ a distância entre elas (a *bitola*), o movimento do robô no plano é:

$$
v = \frac{v_R + v_L}{2} \qquad \omega = \frac{v_R - v_L}{L}
$$

em que $v$ é a velocidade linear do centro do robô e $\omega$ a velocidade angular (positiva no sentido anti-horário). Três casos particulares:

| Comando | $v_R$, $v_L$ | Resultado |
|---|---|---|
| `forward(50)` | iguais | $\omega = 0$: linha reta |
| `move(60, 40)` | diferentes, mesmo sinal | curva de raio $R = v/\omega$ |
| `move(-40, 40)` | opostas | $v = 0$: giro no próprio eixo |

A pose do robô $(x, y, \theta)$ evolui segundo:

$$
\dot{x} = v\cos\theta \qquad \dot{y} = v\sin\theta \qquad \dot{\theta} = \omega
$$

Integrar essas equações a partir das velocidades comandadas é a **odometria por *dead reckoning***: estimar onde o robô está sem olhar para o ambiente.

### Malha aberta

Na RoverLib, a velocidade é a **porcentagem do PWM** enviada a cada motor (0 a 100), e não uma velocidade em m/s. Ninguém mede se a roda girou o que deveria: o comando é enviado e o programa confia no resultado. Isso é controle em **malha aberta**.

A malha aberta funciona enquanto o modelo é fiel ao robô. Na prática, ele nunca é:

- dois motores "iguais" giram em velocidades diferentes com o mesmo PWM;
- a velocidade depende da carga da bateria, do piso e do atrito;
- a relação entre PWM e velocidade não é linear (há uma zona morta perto de zero);
- os erros de direção se **acumulam**: um desvio de 2° por giro vira 8° num quadrado.

A `Calibration` da RoverLib compensa a primeira causa, multiplicando a velocidade de cada lado por um fator (`calibration.right` e `calibration.left` no `config.yaml`). As outras só se resolvem **medindo** o resultado, o que é o assunto das aulas 2 e 5.

!!! note "Um caso real no Rover"
    O servo do PAN da câmera é de rotação contínua: como as rodas, ele recebe uma velocidade e não informa a posição. Nos testes do projeto, estimar o ângulo por "velocidade × tempo" errou mais de 50° em poucos movimentos, porque a velocidade real variava com o esforço do cabo e com o tempo de partida do servo. É o mesmo fenômeno desta aula.

## Prática

Os scripts estão em `tutoriais/aula1_locomocao/`. Execute-os a partir da pasta `tutoriais/`.

### 1. Primeiros comandos

```bash
python aula1_locomocao/primeiros_comandos.py
```

```python
with Rover.from_config(CONFIG) as rover:
    rover.move.forward(speed=50, duration=1)
    rover.move.turn_right(speed=50, duration=0.5)
    rover.move.move(speed_right=60, speed_left=30, duration=1)   # curva para a esquerda
    rover.move.move(speed_right=-40, speed_left=40, duration=1)  # giro no próprio eixo
    rover.move.backward(speed=40, duration=1)
```

No PC, cada mudança de velocidade aparece no terminal (`[simulação] esquerdo: Frente - velocidade: 50`). O `with` garante que os motores param ao final, mesmo se o programa for interrompido com Ctrl+C.

### 2. Prevendo trajetórias

O script `cinematica.py` integra o modelo pelo método de Euler, com passo $\Delta t = 10$ ms:

```python
v = (v_r + v_l) / 2
omega = (v_r - v_l) / BITOLA
for _ in range(passos):
    x += v * math.cos(theta) * DT
    y += v * math.sin(theta) * DT
    theta += omega * DT
```

```bash
python aula1_locomocao/cinematica.py
```

Ele simula três casos e salva a figura `aula1_locomocao/saida/trajetorias.png`:

- um **quadrado ideal**, que fecha no ponto de partida;
- o **mesmo quadrado com o motor direito 5% mais lento**, que termina a cerca de 10 cm da origem e 25° fora da direção inicial;
- um **círculo** com `move(60, 40)`.

O terminal também mostra o tempo de giro de 90° previsto pelo modelo. Os parâmetros `VEL_MAX` (velocidade de uma roda a 100%) e `BITOLA` são **estimativas**: no robô, eles devem ser medidos (exercício 3).

### 3. Polígono por tempo

```bash
python aula1_locomocao/poligono.py
```

O script percorre um pentágono com `turn_degrees(72)`. O `turn_degrees()` não mede o ângulo: ele converte graus em tempo, usando `time_to_turn`, o tempo que o Rover leva para dar uma volta completa. Se esse valor estiver errado, todos os giros erram na mesma proporção.

## Exercícios

⭐ **1. Polígonos.** Altere `poligono.py` para desenhar um triângulo e um hexágono. Qual o ângulo de giro em cada vértice? Generalize para $N$ lados.

⭐ **2. Raio da curva.** Pelo modelo, qual o raio da curva produzida por `move(60, 40)`? Confira com a figura do `cinematica.py`. Que par de velocidades produz um círculo de 50 cm de raio?

⭐⭐ **3. Medindo o robô.** No `cinematica.py`, `VEL_MAX` e `BITOLA` são palpites. Descreva um experimento para medir cada um no Rover usando apenas uma trena e um cronômetro. *(Dica: ande em linha reta por um tempo conhecido; depois, gire no próprio eixo e conte as voltas.)*

⭐⭐ **4. Oito.** Escreva a sequência de comandos `move()` que desenha um "8" e verifique no simulador antes de rodar no robô.

⭐⭐⭐ **5. Sensibilidade ao erro.** Usando `simular()`, varie `fator_direita` de 0.90 a 1.00 e meça a distância entre a posição final e a origem depois de 1, 2 e 4 voltas no quadrado. Faça um gráfico. O erro cresce linearmente com o número de voltas? Por quê?

⭐⭐⭐ **6. Calibração pelo desvio.** Suponha que, ao andar 2 m em linha reta, o Rover termine 15 cm à esquerda do alvo. Use o modelo para estimar o fator de calibração do lado direito que corrige esse desvio e explique as hipóteses da sua estimativa.

## No Rover

- Comece com o Rover **suspenso** (rodas fora do chão) para conferir os sentidos de giro.
- Meça `time_to_turn` (exercício 3) e use o valor medido em `turn_degrees()`. O valor padrão (12 s) é só um ponto de partida.
- Ajuste `calibration` no `config.yaml` até o Rover andar reto por 2 m. Se ele puxa para a esquerda, o motor direito está mais rápido: reduza `calibration.right`.
- Compare o pentágono real com o previsto: a diferença é o erro da malha aberta.

## Para saber mais

- SIEGWART, R.; NOURBAKHSH, I.; SCARAMUZZA, D. *Introduction to Autonomous Mobile Robots*, cap. 3 (cinemática de robôs móveis) e cap. 5 (odometria e seus erros).
- Referência da API: [`Robot`](../api/movimento.md) e [`Calibration`](../api/movimento.md).
