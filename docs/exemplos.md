# Exemplos

## Exemplos do `rover new`

Todo projeto criado com `rover new` traz exemplos curtos em `src/examples/`, pensados para um primeiro contato. Execute-os dentro da pasta do projeto:

| Comando | O que faz | Precisa de |
|---|---|---|
| `python -m src.examples.quadrado` | Percorre um quadrado | motores |
| `python -m src.examples.cor_vermelha` | Destaca objetos vermelhos na imagem | seção `camera:` |
| `python -m src.examples.parar_no_obstaculo` | Anda e para perto de obstáculos | seção `lidar:` |

## Projetos completos

A pasta [`examples/`](https://github.com/Rover-Project/Rover/tree/main/examples) do repositório traz aplicações maiores. Cada uma tem `main.py`, `config.yaml` e `src/`, e é executada dentro da sua pasta:

```bash
cd examples/circleDetect
python main.py
```

### Visão computacional

| Exemplo | O que faz | Hardware |
|---|---|---|
| `circleDetect` | Detecta círculos vermelhos combinando Hough e contornos, com suavização entre frames | câmera ou webcam |
| `lineDetect` | Segue uma pista (duas linhas) ou uma linha única com controle proporcional | câmera + motores |
| `folowCircle` | Persegue uma bola vermelha usando PID na posição e no tamanho do círculo | câmera + motores |
| `objectDetection` | Detecta objetos com YOLOv8n (requer `pip install roverlib[ai]`) | câmera |
| `mediaPiper` | Reconhecimento de gestos com MediaPipe (requer `pip install roverlib[ai]`) | câmera |

### Câmera

| Exemplo | O que faz | Hardware |
|---|---|---|
| `continuousFocus` | Foco automático contínuo e captura de fotos | Camera Module 3 |
| `slideFocus` | Ajuste manual do foco pelo teclado | Camera Module 3 |

### Sensores

| Exemplo | O que faz | Hardware |
|---|---|---|
| `lidarGraph` | Gráfico em tempo real de distância, força do sinal e temperatura | Lidar TF-Luna |
| `lidarAvoidance` | Desvia de obstáculos com o Lidar e uma máquina de estados | Lidar + motores |

### Controle manual

| Exemplo | O que faz | Hardware |
|---|---|---|
| `roverKeypadControl` | Dirige o Rover pelo teclado, com visualização da câmera | motores + câmera |
| `roverTkControl` | Interface gráfica (Tkinter) para testar os motores | motores |
| `servoMotor`, `servoController`, `servos_controller` | Controle de servos (pan-tilt da câmera) | servos / PCA9685 |

!!! note "Exemplos sem simulação"
    Os projetos completos foram escritos para o Rover e criam `Camera` e `Robot` diretamente. Os que usam só motores rodam no PC em modo simulação; os que usam `Camera`, Lidar ou servos precisam do hardware.
