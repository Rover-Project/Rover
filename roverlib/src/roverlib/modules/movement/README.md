# Módulo de Movimento

Controle de alto nível dos dois motores DC do Rover (ponte-H L298N).

## Estrutura

```
movement/
├── robot.py             # Robot: comandos de movimento
├── motorCalibration.py  # Calibration: compensa diferenças entre os motores
├── PID.py               # PID: controladores P, PD e PID
└── tests/               # testes (rodam sem hardware)
```

O `Robot` usa os drivers de `plugins/motor/`:

- `MotorDriver`: motor real, via plugin `pin` (GPIO/PWM da Raspberry Pi);
- `VirtualMotor`: motor simulado, que só registra e imprime os comandos.

## Uso

Pela classe `Rover` (recomendado), o `Robot` é `rover.move`:

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.move.forward(50, duration=2)
```

Ou diretamente:

```python
from roverlib import Robot, Calibration

with Robot(right=(17, 26), left=(25, 16), calibration=Calibration(right=1, left=0.95)) as robot:
    robot.forward(50, duration=2)               # frente por 2 s e para
    robot.turn_left(50, duration=0.5)           # gira no próprio eixo
    robot.move(speed_right=60, speed_left=30)   # curva: cada lado com sua velocidade
    robot.stop()
```

| Método | Descrição |
|---|---|
| `forward(speed=50, duration=None)` | Anda para frente |
| `backward(speed=50, duration=None)` | Anda para trás |
| `turn_left(speed=50, duration=None)` | Gira para a esquerda no próprio eixo |
| `turn_right(speed=50, duration=None)` | Gira para a direita no próprio eixo |
| `move(speed_right, speed_left, duration=None)` | Velocidade de cada lado; negativo gira a roda para trás, `0` para |
| `turn_degrees(degrees, time_to_turn=12, turn_speed=55)` | Gira por ângulo, estimado por tempo (positivo: direita) |
| `stop()` | Para os motores |
| `cleanup()` | Para e libera a GPIO (chamado automaticamente pelo `with`) |

Velocidades vão de 0 a 100. Com `duration`, o movimento dura esse tempo e o Rover para; sem `duration`, continua até o próximo comando.

### `turn_degrees`

O Rover não tem encoder nas rodas, então o ângulo é estimado por tempo: `duração = graus / 360 × time_to_turn`. Meça quantos segundos o seu Rover leva para dar uma volta completa com `turn_speed` e passe esse valor em `time_to_turn`.

## Calibração

Motores iguais raramente giram na mesma velocidade. `Calibration(right, left)` multiplica a velocidade de cada lado: se o Rover puxa para a esquerda em `forward()`, o motor direito está mais rápido, então reduza `right` (ex.: `0.95`).

A calibração é aplicada em `forward()`, `backward()` e `move()`. No `config.yaml`:

```yaml
motors:
  calibration:
    right: 0.95
    left: 1
```

## Modo simulação

Sem Raspberry Pi (ou sem o plugin `pin` compilado), o `Robot` usa automaticamente motores simulados (`VirtualMotor`): os comandos aparecem no terminal e nada é enviado à GPIO.

- `Robot(..., simulate=True)`: sempre simula.
- `Robot(..., simulate=False)`: exige o hardware (erro se a GPIO não estiver disponível).
- `ROVER_SIMULATE=1 python main.py`: força a simulação sem alterar o código (útil para testar na RPi sem mover as rodas).
- `robot.simulated` indica o modo em uso.

Em modo simulação, o estado de cada motor fica em `robot.left_motor.speed` e `robot.left_motor.direction` (idem para `right_motor`), o que permite testar programas automaticamente.

## PID

```python
from roverlib import PID

pid = PID(kp=0.4, ki=0.0, kd=0.1)
correcao = pid.controller_PID(erro)   # também: controller_P, controller_PD
robot.move(speed_right=base + correcao, speed_left=base - correcao)
```

## Testes

Na pasta `roverlib/`:

```bash
python -m pytest src/roverlib/modules/movement/tests
```
