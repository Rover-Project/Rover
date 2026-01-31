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

## 🧪 Testes

Execute os testes com:
```bash
python3 tests/test_movement.py --test all
python3 tests/test_movement.py --calibrate
```

Veja `tests/INSTRUCOES_TESTE.md` para detalhes completos.

