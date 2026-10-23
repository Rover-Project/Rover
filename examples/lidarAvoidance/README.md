# AvoidObject: Prevenção de Colisão e Navegação Lidar

Este exemplo demonstra como utilizar o sensor Lidar TF-Luna integrado com a biblioteca `roverlib` para construir um sistema autônomo de prevenção de colisões. O Rover monitora obstáculos e utiliza um sistema de decisão baseado em estados e controle PID para desviar de barreiras físicas.

## Arquitetura e Estrutura de Diretórios

```text
avoidObject/
│
├── config.yaml
├── main.py
├── README.md
└── src/
    ├── __init__.py
    └── avoider.py
