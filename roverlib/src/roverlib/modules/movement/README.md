# Módulo de Movimento - Estrutura Modular

Este módulo foi reorganizado em uma estrutura modular com três camadas de abstração.

## 📁 Estrutura

```
movement/
├── __init__.py      # Exporta as classes principais
├── driver.py        # Camada baixa: GPIO/PWM direto
├── commands.py      # Camada média: Comandos básicos
└── control.py       # Camada alta: Controle com calibração
```

## 🔧 Camadas

### 1. MotorDriver (`driver.py`)
**Nível mais baixo** - Comunicação direta com hardware
- Gerencia pinos GPIO
- Controla sinais PWM
- Sem lógica de negócio

**Uso:**
```python
from rover_lib.modules.movement import MotorDriver

driver = MotorDriver(pwm_frequency=100)
driver.initialize()
driver.set_motor_left('forward', 50)
driver.set_motor_right('forward', 50)
driver.cleanup()
```

### 2. MovementCommands (`commands.py`)
**Nível médio** - Comandos intuitivos
- Interface simplificada
- Comandos: forward, backward, turn_left, turn_right
- Suporta duração automática

**Uso:**
```python
from rover_lib.modules.movement import MovementCommands

movement = MovementCommands()
movement.forward(speed=50, duration=2)  # Move por 2 segundos
movement.turn_left(speed=40, duration=1)
movement.cleanup()
```

### 3. MovementControl (`control.py`)
**Nível alto** - Controle avançado
- Tudo do MovementCommands
- Calibração de motores
- Compensação automática
- Persistência de configuração

**Uso:**
```python
from rover_lib.modules.movement import MovementControl

control = MovementControl()
control.forward(speed=50, use_calibration=True)
control.calibrate_motors(left_bias=1.05, right_bias=0.95)
control.cleanup()
```

## 🔄 Compatibilidade

O arquivo `movement.py` original foi mantido para compatibilidade:
```python
from rover_lib.modules.movement import MovementModule  # Funciona como antes
```

## 📝 Calibração

A calibração é salva em `motor_calibration.json`:
```json
{
  "left_motor_bias": 1.0,
  "right_motor_bias": 1.0,
  "min_speed_threshold": 5.0
}
```

## 🖥️ Modo simulação

Sem Raspberry Pi (ou sem o plugin `pin` compilado), o `Robot` usa automaticamente motores simulados (`VirtualMotor`): os comandos aparecem no terminal e nada é enviado à GPIO.

```python
from roverlib.modules.movement.robot import Robot

with Robot(right=(17, 27), left=(22, 23)) as robot:   # simula no PC, real na RPi
    robot.forward(50, duration=2)
    print(robot.simulated)
```

- `Robot(..., simulate=True)`: sempre simula.
- `Robot(..., simulate=False)`: exige o hardware (erro se a GPIO não estiver disponível).
- `ROVER_SIMULATE=1 python main.py`: força a simulação sem alterar o código (útil para testar na RPi sem mover as rodas).

## 🧪 Testes

Na pasta `roverlib/`:
```bash
python -m pytest src/roverlib/modules/movement/tests
```
