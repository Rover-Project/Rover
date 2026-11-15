# Aprender com o Rover

Trilha de seis aulas para disciplinas de **visão computacional, robótica e inteligência artificial**. Cada aula parte de um conceito da área, mostra como ele aparece no Rover e termina com exercícios e um desafio. O mesmo código roda no PC, com motores e Lidar simulados, e no robô.

## Para quem é

Estudantes que já programam em Python (funções, laços, classes) e conhecem o básico de NumPy. Não é preciso conhecer o hardware: a RoverLib cuida de GPIO, PWM, porta serial e câmera.

## As aulas

| Aula | Tema | Conceitos | Precisa de |
|---|---|---|---|
| [1](aula1-locomocao.md) | Locomoção diferencial e malha aberta | modelo cinemático, odometria, erro acumulado, calibração | só o PC |
| [2](aula2-sensores.md) | Sensores de distância, ruído e máquinas de estados | modelo do sensor, filtros de média e mediana, histerese, FSM | só o PC |
| [3](aula3-imagem.md) | Imagem digital e espaços de cor | imagem como matriz, BGR/RGB/HSV, limiarização, morfologia | só o PC (webcam opcional) |
| [4](aula4-deteccao.md) | Detecção de objetos por cor e forma | contornos, momentos, circularidade, Transformada de Hough, avaliação quantitativa | só o PC (webcam opcional) |
| [5](aula5-controle.md) | Controle realimentado por visão | malha fechada, controladores P, PI e PID, saturação, zona morta, sintonia | só o PC (webcam opcional) |
| [6](aula6-projeto.md) | Projeto integrador | arquitetura reativa, integração de percepção e controle | PC; Rover para a apresentação |

Cada aula foi pensada para cerca de **2 horas**: 30 minutos de conceitos, 60 de prática guiada e 30 para os exercícios. As aulas 1 e 2 e as aulas 3 e 4 também funcionam em pares, para quem tiver menos encontros.

## Preparação

1. Instale a RoverLib no PC (veja [Instalação](../instalacao.md)).
2. Baixe o repositório, que contém o código das aulas na pasta `tutoriais/`:

    ```bash
    git clone https://github.com/Rover-Project/Rover.git
    cd Rover/tutoriais
    ```

3. Rode o primeiro script para conferir:

    ```bash
    python aula1_locomocao/primeiros_comandos.py
    ```

    No PC, o terminal mostra os motores simulados. As figuras geradas pelas aulas são salvas na pasta `saida/` de cada aula.

As aulas 1 e 2 leem o `tutoriais/config.yaml` (motores e Lidar); as aulas 3 a 6 leem o `tutoriais/config_visao.yaml`, que acrescenta a câmera. No Rover, os mesmos arquivos usam o hardware real; para rodar no robô sem mover as rodas, use `ROVER_SIMULATE=1 python ...`.

## Como as aulas são organizadas

- **Objetivos:** o que o estudante deve saber fazer ao final.
- **Conceitos:** a teoria necessária, com as equações e referências.
- **Prática:** passos com o código da pasta `tutoriais/`, que o estudante executa e modifica.
- **Exercícios:** em três níveis: ⭐ aplicar, ⭐⭐ modificar, ⭐⭐⭐ investigar.
- **No Rover:** o que muda ao levar o experimento para o robô.
- **Para saber mais:** leituras de aprofundamento.

## Referências gerais

- SZELISKI, Richard. *Computer Vision: Algorithms and Applications*. 2. ed. Springer, 2022.
- SIEGWART, Roland; NOURBAKHSH, Illah; SCARAMUZZA, Davide. *Introduction to Autonomous Mobile Robots*. 2. ed. MIT Press, 2011.
- ÅSTRÖM, Karl J.; MURRAY, Richard M. *Feedback Systems: An Introduction for Scientists and Engineers*. 2. ed. Princeton University Press, 2021.
- RUSSELL, Stuart; NORVIG, Peter. *Artificial Intelligence: A Modern Approach*. 4. ed. Pearson, 2021.
