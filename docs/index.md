# Bem-vindo à RoverLib

A **RoverLib** é uma biblioteca modular em Python para **Raspberry Pi 5**, projetada especificamente para viabilizar arquiteturas de robótica baseadas em **Code as Policies**.

!!! info "Conceito Central"
    Diferente de robôs teleoperados clássicos, aqui o **humano define o "O Quê"** (o objetivo em linguagem natural) e um **LLM gera o "Como"** (código Python que chama esta API).

---

## Como Funciona

A biblioteca abstrai a complexidade de drivers de hardware (PWM, I2C, CSI) em comandos de alto nível que LLMs conseguem entender e orquestrar.

### Exemplo de Code as Policies

=== "🗣️ Prompt do Usuário"
    > "Ande para frente por 2 segundos e depois procure por uma bola vermelha. Se encontrar, me avise."

=== " Código Gerado (LLM)"
    ```python
    from rover_lib import Rover

    # Inicializa o robô (Drivers, Câmera e Visão)
    rover = Rover()

    # 1. Executa movimento temporal
    rover.movement.forward(speed=50, duration=2.0)

    # 2. Captura e analisa o ambiente
    frame = rover.camera.get_frame()
    
    # 3. Usa visão computacional clássica (híbrida)
    circle = rover.vision.circleCannyDetect(frame)

    if circle:
        print(f"Objeto encontrado em: {circle}")
    
    rover.stop_and_cleanup()
    ```

---

## Características Principais

* **Arquitetura em Camadas:** Separação clara entre Hardware (Drivers), Comportamento (Robot) e Inteligência (LLM).
* **Visão Híbrida:** Algoritmos clássicos otimizados (Hough, Canny, HSV) rodando a **30 FPS** na CPU da RPi 5.
* **Loop de Controle em Tempo Real:** Ciclo de decisão de 10ms para tarefas críticas como *Line Following*.
* **Fallbacks Automáticos:** Se a câmera oficial (Picamera2) não for detectada, o sistema alterna para um *Mock* de webcam automaticamente para facilitar testes no PC.

## Instalação

```bash
git clone [https://github.com/Rover-Project/Rover.git](https://github.com/Rover-Project/Rover.git)
cd Rover
pip install -r requirements.txt