# Aula 5: Controle realimentado por visão

Nas aulas anteriores, o Rover se movia por tempo (aula 1), reagia a limites fixos (aula 2) e aprendeu a encontrar um objeto na imagem (aulas 3 e 4). Agora essas peças se juntam numa **malha fechada**: a cada quadro, o robô mede onde o objeto está e corrige o movimento para mantê-lo no centro. Você vai sintonizar controladores numa simulação antes de levá-los ao robô.

## Objetivos

Ao final da aula, você deve ser capaz de:

- montar uma malha de controle com sensor (câmera), controlador e atuador (motores);
- explicar o efeito de cada parcela do PID e os fenômenos de erro estacionário, sobressinal e oscilação;
- lidar com não linearidades reais: saturação, zona morta e atraso;
- sintonizar um controlador por simulação e medir seu desempenho.

## Conceitos

### A malha fechada

```
              erro e(t)              comando u(t)
 referência ──▶(+)──▶ Controlador ──────────────▶ Motores ──▶ Rover gira
 (centro)       ▲ −                                               │
                └──────── posição do objeto na imagem ◀── Câmera ◀┘
```

O **erro** é a posição horizontal do centroide do objeto, normalizada:

$$
e = \frac{\bar{x} - L/2}{L/2} \in [-1, 1]
$$

em que $L$ é a largura da imagem. $e > 0$ significa objeto à direita, e o robô deve girar para a direita.

### O controlador PID

$$
u(t) = K_p\, e(t) + K_i \int_0^t e(\tau)\, d\tau + K_d\, \frac{de(t)}{dt}
$$

| Parcela | Efeito | Problema se exagerada |
|---|---|---|
| Proporcional $K_p$ | corrige mais quanto maior o erro | sobressinal e oscilação |
| Integral $K_i$ | acumula o erro passado e elimina o erro que sobra | lentidão para "esvaziar" a integral (*windup*), oscilação lenta |
| Derivativa $K_d$ | antecipa a tendência e amortece | amplifica o ruído da medida |

Na implementação discreta, a cada quadro (passo $\Delta t$): a integral é a soma $\sum e_k \Delta t$ e a derivada é $(e_k - e_{k-1}) / \Delta t$. O controlador da aula (`tutoriais/aula5_controle/controlador.py`) recebe o $\Delta t$ explicitamente, satura a saída e limita a integral (**anti-windup**). Ele é curto de propósito, para ser lido e modificado nos exercícios. A RoverLib tem uma classe equivalente, [`PID`](../api/movimento.md), com `controller_P()`, `controller_PD()` e `controller_PID(erro, dt)`; a diferença é que ela não satura a saída, o que fica a cargo do programa.

### Não linearidades do Rover

Os livros costumam supor sistemas lineares. O Rover não é:

- **saturação:** a velocidade não passa de 100;
- **zona morta:** abaixo de um certo PWM, o motor não vence o atrito e não gira. Com controle só proporcional, o erro "trava" quando $K_p |e|$ fica menor que a zona morta: sobra um **erro estacionário**;
- **atraso:** a imagem leva pelo menos um quadro (33 ms) para ser capturada e processada, e o motor demora a acelerar. Atraso favorece a oscilação quando o ganho é alto.

## Prática

Os scripts estão em `tutoriais/aula5_controle/`.

### 1. Sintonia na simulação

```bash
python aula5_controle/sintonia.py
```

A simulação modela o Rover girando para centralizar um alvo 30° à direita: câmera *pinhole* com campo de visão de 62°, motor com zona morta e resposta de primeira ordem, e um quadro de atraso na visão. Ela compara cinco controladores e salva `aula5_controle/saida/sintonia.png`:

| Controlador | Sobressinal | Acomodação (±1°) | Erro final |
|---|---|---|---|
| P ($K_p=40$) | 0,0° | não acomoda | 5,6° |
| P ($K_p=250$) | 7,2° | 0,83 s | −0,8° |
| PI ($K_p=40$, $K_i=20$) | 0,0° | 0,73 s | 0,0° |
| PI ($K_p=40$, $K_i=60$) | 9,3° | 3,30 s | −0,3° |
| PID ($K_p=80$, $K_i=30$, $K_d=6$) | 0,4° | 0,57 s | −0,4° |

Leitura do resultado:

- o **P com ganho baixo** para antes do alvo: o comando cai abaixo da zona morta com 5,6° de erro;
- o **P com ganho alto** chega rápido, mas passa do alvo e oscila;
- o **PI** elimina o erro final; com $K_i$ alto demais, ele passa do alvo e demora a voltar, porque a integral precisa "esvaziar" e a zona morta prende o robô;
- o **PID** usa a derivada para amortecer, o que permite um $K_p$ maior sem sobressinal.

### 2. No robô (ou com a webcam)

```bash
python aula5_controle/seguir_objeto.py
```

```python
erro, mascara = erro_horizontal(frame)          # centroide do vermelho
if erro is None:
    rover.move.stop()
    pid.reiniciar()
else:
    u = pid(erro, dt)
    rover.move.move(speed_right=-u, speed_left=u)   # giro no próprio eixo
```

Com uma webcam no PC, os motores são simulados: mova uma bola vermelha diante da câmera e observe os comandos no terminal. No Rover, o robô gira para acompanhá-la. O $\Delta t$ é medido a cada quadro, porque a taxa real de processamento varia.

## Exercícios

⭐ **1. Zona morta.** Na simulação, mude `ZONA_MORTA` para 0 e rode de novo. O P com $K_p=40$ ainda tem erro estacionário? Explique.

⭐ **2. Limite de estabilidade.** Aumente $K_p$ do controlador P até a resposta oscilar sem amortecer. Qual o ganho crítico? Ele muda se você dobrar o atraso da visão (dois quadros)?

⭐⭐ **3. Sintonia de Ziegler-Nichols.** Com o ganho crítico $K_u$ e o período de oscilação $T_u$ do exercício 2, calcule os ganhos do PID pela regra de Ziegler-Nichols ($K_p = 0{,}6K_u$, $K_i = 1{,}2K_u/T_u$, $K_d = 0{,}075K_uT_u$) e compare com os valores da tabela.

⭐⭐ **4. Ruído na medida.** Some ao erro visto um ruído gaussiano com desvio de 0,02 (cerca de 6 px). Compare o PID com e sem a parcela derivativa. Proponha uma solução (por exemplo, filtrar a derivada).

⭐⭐ **5. Alvo em movimento.** Faça o alvo se mover a 10°/s na simulação. Qual controlador mantém o menor erro? Por que a integral ajuda aqui?

⭐⭐⭐ **6. Distância.** No `seguir_objeto.py`, acrescente um segundo controlador que usa a **área** do objeto para avançar ou recuar até uma distância desejada, combinando os dois comandos em `move(speed_right, speed_left)`. Discuta a interação entre as duas malhas.

## No Rover

- Comece com ganhos baixos (por exemplo, $K_p = 30$, $K_i = 0$) e o Rover suspenso; aumente aos poucos.
- A zona morta real depende da bateria e do piso: meça o menor `move()` que faz o Rover girar e use o valor na simulação.
- O processamento da imagem na Raspberry Pi é mais lento que no PC. Meça a taxa de quadros real e repita a sintonia com esse $\Delta t$.
- O exemplo `folowCircle` do repositório aplica a mesma ideia com PID na posição e no raio da bola.

## Para saber mais

- ÅSTRÖM, K. J.; MURRAY, R. M. *Feedback Systems*, 2. ed., cap. 11 (controle PID) e cap. 10 (atrasos e robustez).
- CORKE, Peter. *Robotics, Vision and Control*. 3. ed. Springer, 2023, cap. 15 (*visual servoing*).
- Referência da API: [`Robot.move`](../api/movimento.md) e [`ProcessingImage`](../api/visao.md).
