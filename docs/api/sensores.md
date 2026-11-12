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
