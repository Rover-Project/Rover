# Sensores

## Lidar TF-Luna

Mede a distância de um único ponto à frente do sensor. Pelo `Rover`, é acessado como `rover.lidar`.

A faixa garantida pelo fabricante vai de **0,2 m a 8 m**. Abaixo de 20 cm o sensor ainda responde (nos testes, uma mão a 7–8 cm foi lida corretamente), mas sem precisão garantida: para detectar obstáculos, use limites de 20 cm ou mais em `is_obstacle()`.

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
