# Aula 6: Projeto integrador

O projeto junta tudo o que foi visto na trilha: o Rover deve **encontrar uma bola vermelha, alinhar-se com ela e se aproximar até parar a 30 cm**. Ele envolve locomoção (aula 1), máquina de estados e Lidar (aula 2), segmentação (aula 3), centroide (aula 4) e controle em malha fechada (aula 5).

O projeto é desenvolvido e testado num **mundo simulado** que roda no PC, sem câmera nem robô, e apresentado no Rover real.

## Objetivos

- Projetar a arquitetura de um comportamento autônomo: percepção, decisão e ação.
- Integrar percepção visual, sensor de distância e controle numa máquina de estados.
- Validar o comportamento em simulação antes do robô e explicar as diferenças observadas.

## O mundo simulado

O arquivo `tutoriais/aula6_projeto/mundo.py` simula uma sala com uma bola vermelha de 7 cm:

- a posição e a direção do Rover evoluem pelo **modelo cinemático** da aula 1, a partir das velocidades enviadas às rodas;
- a câmera é um modelo ***pinhole*** (62° de campo de visão): a cada passo, o mundo **gera o frame** que a câmera veria, com a bola desenhada na posição e no tamanho corretos (cena sintética da aula 3);
- o Lidar mede a distância até a bola, quando ela está bem à frente, ou até a parede.

O programa do aluno recebe frames e leituras exatamente como no robô, então o mesmo código de percepção e decisão funciona nos dois casos.

## O esqueleto

```bash
python aula6_projeto/main.py            # no mundo simulado
python aula6_projeto/main.py --real     # com a câmera e o Lidar (Rover, ou webcam no PC)
```

O `main.py` já tem o laço principal e está dividido em três funções:

| Função | Responsabilidade | Situação |
|---|---|---|
| `perceber(frame, distancia)` | segmenta o vermelho e calcula `visto`, `erro`, `area` e `distancia` | pronta |
| `decidir(estado, percepcao)` | transições da máquina de estados | parcial: faltam as transições de `APROXIMAR` (TODO 1 e 2) |
| `agir(estado, percepcao, dt)` | velocidades (direita, esquerda) de cada estado | parcial: falta o movimento de `APROXIMAR` (TODO 3) |

A máquina de estados sugerida:

```
           bola vista            |erro| < 0,08
 BUSCAR ─────────────▶ ALINHAR ─────────────▶ APROXIMAR ───────────▶ CHEGOU
   ▲                      │                       │   distância ≤ 30 cm
   └──── bola perdida ────┴───── bola perdida ────┘
```

Rodando o esqueleto sem alterações, o Rover encontra e alinha com a bola, mas fica parado em `APROXIMAR`:

```
t=  0.0 s  BUSCAR -> ALINHAR   Rover em (0.00, 0.00) m, bola a 1.70 m e +28°
t=  0.9 s  ALINHAR -> APROXIMAR   Rover em (0.00, 0.00) m, bola a 1.70 m e +2°
```

## Etapas

1. **Completar o comportamento básico.** Implemente os TODOs até o Rover terminar em `CHEGOU`, a cerca de 30 cm da bola. *Dica para o TODO 3:* some à velocidade base uma correção de giro proporcional ao erro, como na aula 5: `return base - c, base + c`, com `c = k * erro`.
2. **Tornar o comportamento robusto.** Teste o comportamento em situações difíceis, alterando o `MundoSimulado`:
    - bola atrás do robô, fora do campo de visão;
    - bola longe (3 m), que aparece pequena na imagem;
    - ruído na leitura do Lidar e leituras inválidas (`None`).
3. **Medir.** Para 10 posições aleatórias da bola, registre se o Rover chegou, o tempo gasto e a distância final. Compare duas versões do seu controlador.
4. **Levar ao robô.** Rode com `--real`. Ajuste ganhos, velocidades e o limiar de área com o Rover e anote o que precisou mudar em relação à simulação.

## Entregas

- Código do projeto (`main.py` e eventuais módulos novos), comentado.
- Diagrama da máquina de estados final, com as condições de cada transição.
- Relatório curto (até 4 páginas) com: arquitetura, decisões de projeto, resultados das medições da etapa 3 e diferenças entre simulação e robô.
- Demonstração no Rover.

## Critérios de avaliação

| Critério | Peso | O que se espera |
|---|---|---|
| Funcionamento na simulação | 25% | chega à bola nas situações da etapa 2 |
| Funcionamento no robô | 25% | encontra, alinha e para perto da bola na demonstração |
| Arquitetura e código | 20% | estados bem definidos, percepção, decisão e ação separadas, código legível |
| Avaliação experimental | 20% | medições da etapa 3 com método claro e resultados interpretados |
| Análise simulação × robô | 10% | diferenças identificadas e explicadas (atrasos, zona morta, iluminação...) |

## Extensões

Para grupos que terminarem antes, ou como projeto de maior duração:

- **Desvio de obstáculos:** acrescente uma caixa entre o Rover e a bola no mundo simulado e um estado `DESVIAR`, usando o Lidar como na aula 2.
- **Busca com a câmera:** no Rover, use o pan-tilt (`rover.pan_tilt`) para procurar a bola girando só a câmera antes de girar o robô.
- **Várias bolas:** com bolas de cores diferentes, visite-as numa ordem definida.
- **Detector melhor:** substitua o centroide pela combinação Hough + contorno da aula 4 e meça o efeito com a avaliação da etapa 3.
- **Aprendizado:** troque a segmentação por cor por um detector treinado (o exemplo `objectDetection` usa YOLOv8).

## No Rover

- Faça a primeira execução com `ROVER_SIMULATE=1 python aula6_projeto/main.py --real`: a câmera é real, mas os motores e o Lidar são simulados. Assim, é possível conferir a percepção sem o robô andar.
- Garanta espaço livre em volta do Rover e mantenha a mão perto do teclado para interromper com Ctrl+C: o `with` para os motores.
- A distância do Lidar é medida no centro do sensor; se a bola for pequena, ela pode não estar exatamente à frente dele. Use também a área da bola na imagem como critério de chegada.

## Para saber mais

- SIEGWART, R.; NOURBAKHSH, I.; SCARAMUZZA, D. *Introduction to Autonomous Mobile Robots*, cap. 6 (planejamento e navegação).
- ARKIN, R. C. *Behavior-Based Robotics*, MIT Press, 1998.
- Exemplos completos do repositório: [Exemplos](../exemplos.md), em especial `folowCircle`, `lidarAvoidance` e `cameraTracking`.
