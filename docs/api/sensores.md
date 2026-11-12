# Sensores

## Lidar TF-Luna

Mede a distância de um único ponto à frente do sensor (0,2 m a 8 m). Pelo `Rover`, é acessado como `rover.lidar`.

```python
from roverlib import Lidar

with Lidar() as lidar:
    if lidar.is_obstacle(30):
        print("Obstáculo a menos de 30 cm!")
```

::: roverlib.plugins.lidar.lidar.Lidar

## Lidar simulado

Usado pelo `rover.lidar` fora da Raspberry Pi. A distância é a que você definir com `set_distance()`.

```python
rover.lidar.set_distance(20)     # simula um obstáculo a 20 cm
rover.lidar.is_obstacle(30)      # True
```

::: roverlib.plugins.lidar.virtual.VirtualLidar
