# Primeiro projeto

Este tutorial leva cerca de 10 minutos e funciona **no PC**, sem o Rover: os motores são simulados e cada comando aparece no terminal. Depois, o mesmo projeto roda na Raspberry Pi movendo o robô de verdade.

Pré-requisito: a RoverLib instalada (veja [Instalação](instalacao.md)).

## 1. Crie o projeto

```bash
rover new meu_projeto
cd meu_projeto
```

O comando cria esta estrutura:

```
meu_projeto/
├── main.py          # programa principal: comece por aqui
├── config.yaml      # pinos dos motores, câmera e Lidar
├── README.md
└── src/
    └── examples/    # exemplos curtos para estudar e adaptar
```

## 2. Execute

```bash
rover run
```

No PC, a saída mostra os motores simulados:

```
AVISO: GPIO (plugin pin) não disponível. Usando motores simulados. ...
[simulação] Motor esquerdo inicializado. Pinos: (25, 16)  Frequência PWM: 1000Hz
[simulação] Motor direito inicializado. Pinos: (17, 26)  Frequência PWM: 1000Hz
Rover(motores simulados)
[simulação] esquerdo: Frente - velocidade: 50
[simulação] direito: Frente - velocidade: 50
...
```

## 3. Entenda o `main.py`

```python
from pathlib import Path

from roverlib import Rover

CONFIG = Path(__file__).parent / "config.yaml"


def main():
    with Rover.from_config(CONFIG) as rover:
        print(rover)

        # Velocidades vão de 0 a 100; duration é o tempo em segundos
        rover.move.forward(speed=50, duration=1)
        rover.move.turn_right(speed=50, duration=0.5)
        rover.move.backward(speed=50, duration=1)
```

- `Rover.from_config(...)` lê o `config.yaml` e prepara os componentes (motores, câmera, Lidar).
- `with ... as rover:` garante que, ao final (ou em caso de erro), os motores param e os recursos são liberados.
- `rover.move` controla o movimento. Com `duration`, o Rover executa o movimento por esse tempo e para. Sem `duration`, continua até o próximo comando.

## 4. Modifique

Troque o conteúdo do `with` por um zigue-zague e execute de novo com `rover run`:

```python
    with Rover.from_config(CONFIG) as rover:
        for _ in range(3):
            rover.move.move(speed_right=60, speed_left=30, duration=1)  # curva para a esquerda
            rover.move.move(speed_right=30, speed_left=60, duration=1)  # curva para a direita
```

`move()` define a velocidade de cada lado separadamente. Valores negativos giram a roda para trás.

## 5. Use a câmera

No `config.yaml`, remova os `#` da seção `camera:`:

```yaml
camera:
  width: 640
  height: 480
  fps: 30
  webcam: auto
```

E execute o exemplo que destaca objetos vermelhos (pressione `q` para sair):

```bash
python -m src.examples.cor_vermelha
```

No PC, a imagem vem da webcam; na Raspberry Pi, da câmera do Rover.

!!! tip "Esqueceu de ativar a seção?"
    Usar `rover.camera` sem a seção `camera:` gera a mensagem
    *"rover.camera não foi configurado. Adicione a seção 'camera:' ao config.yaml."*

## 6. Rode no Rover

Copie a pasta do projeto para a Raspberry Pi (ou crie-a lá com `rover new`) e execute:

```bash
rover run
```

Agora sem o aviso de simulação: os motores se movem. Para testar sem que as rodas girem:

```bash
ROVER_SIMULATE=1 rover run
```

## Próximos passos

- [Configuração](configuracao.md): todas as opções do `config.yaml` (pinos, calibração, câmera, Lidar).
- [Exemplos](exemplos.md): projetos completos, como seguir uma linha ou uma bola vermelha.
- [Referência da API](api/rover.md): todos os comandos disponíveis.
