# Rover

A classe `Rover` é o ponto de entrada da RoverLib: lê o `config.yaml` e monta os componentes configurados. Veja [Configuração](../configuracao.md) para o formato do arquivo.

```python
from roverlib import Rover

with Rover.from_config("config.yaml") as rover:
    rover.move.forward(50, duration=2)
```

::: roverlib.rover.Rover

::: roverlib.rover.ComponentNotAvailable
