# Changelog

Mudanças da RoverLib, da mais recente para a mais antiga. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e as versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.2.0] - não lançada

A versão 0.2.0 transforma a RoverLib de um conjunto de drivers em uma biblioteca de uso direto: um único objeto `Rover` lido de um `config.yaml`, o mesmo código no PC (simulação) e no robô, projetos prontos com `rover new` e documentação completa. Também troca o controle de GPIO por um módulo próprio compatível com a Raspberry Pi 5, acrescenta o pan-tilt da câmera e o Lidar TF-Luna, e corrige diversos erros encontrados nos testes com o robô.

Branch: `integration/merge-branches` (526 commits desde a 0.1.0).

### Adicionado

**Uso da biblioteca**

- Classe `Rover`, ponto de entrada único: `Rover.from_config("config.yaml")` monta só os componentes presentes no arquivo e os expõe como `rover.move`, `rover.camera`, `rover.lidar` e `rover.pan_tilt`. Funciona com `with`, que para os motores e libera os recursos ao sair.
- `config.yaml` com as seções `motors`, `camera`, `lidar` e `pan_tilt`; seção vazia usa os valores padrão. O formato antigo dos exemplos (`gpio: motor:`) continua aceito.
- **Modo simulação:** fora da Raspberry Pi, os motores (`VirtualMotor`), os servos (`VirtualServo`, `VirtualContinuousServo`) e o Lidar (`VirtualLidar`) são simulados, e a câmera usa a webcam. Pode ser forçado com `simulate: true` no config ou com a variável `ROVER_SIMULATE=1`.
- `open_camera()`: escolhe sozinha entre a câmera da Raspberry Pi e a webcam.
- Mensagens de erro voltadas ao aluno, como *"rover.camera não foi configurado. Adicione a seção 'camera:' ao config.yaml."*
- Exceção base `RoverLibError` e `HardwareNotAvailable`; todas as exceções da biblioteca herdam delas e também da exceção padrão do Python que já usavam.
- Importação sob demanda: `from roverlib import Rover, Robot, PanTilt, ...` só carrega OpenCV, câmera e GPIO quando usados.
- `Config.get(chave, padrao)` aceita um valor padrão.

**Linha de comando**

- `rover new <nome>` cria um projeto pronto: `main.py`, `config.yaml` comentado, README e exemplos curtos (`quadrado`, `cor_vermelha`, `parar_no_obstaculo`).
- `rover run` executa o projeto a partir da sua pasta.

**Hardware**

- Plugin `pin`: controle de GPIO e PWM em C++ (pybind11), escrito para a Raspberry Pi 5, com escrita e leitura digital, PWM por hardware (pinos 12, 13, 18, 19) e PWM por software em qualquer pino.
  - O módulo nativo é **compilado pelo `pip install`** na Raspberry Pi, para a versão de Python em uso. No PC não é compilado e a biblioteca segue em modo simulação; se a compilação falhar, a instalação continua e um aviso explica como resolver.
  - O endereço dos pinos no sistema é descoberto pelo modelo da placa (Pi 5: 571; Pi 4: 512), em vez de fixo; `gpio_base()` mostra o valor e `ROVER_GPIO_BASE` o força.
- Driver `MotorDriver` para motores DC com ponte-H L298N, construído sobre o plugin `pin`.
- Lidar TF-Luna (UART): leitura contínua em segundo plano, `get_distance(unit)`, `is_obstacle(limite_cm)`, verificação de checksum e desligamento por temperatura.
- Pan-tilt da câmera com dois servos em um PCA9685 (I²C), pela classe `PanTilt` (`rover.pan_tilt`):
  - TILT (servo 180°): `tilt_to()`, `tilt_up()`, `tilt_down()`, movimento suave, limites e inversão.
  - PAN (servo 360°): `pan()`, `pan_left()`, `pan_right()`, `pan_to()`, `pan_degrees()`, posição estimada por velocidade × tempo, limites de giro (`pan.min`/`pan.max`), correção de parada (`trim`) e calibração por sentido.
  - Ao encerrar, a câmera volta para a frente e o TILT continua segurando a câmera (`tilt.hold`).
- Plugin `PCAServos` com as bibliotecas da Adafruit: `Servo` (posição), `ContinuousServo` (rotação contínua) e versões simuladas. `PCAServos.close(keep_channels=...)` mantém canais ativos após fechar.
- Câmera: `AfCamera` com controle de foco (contínuo, automático e manual) para módulos com autofoco, como a Arducam IMX519 do Rover.
- Formato de cor dos frames: `set_format()` na `Camera` e na `Webcam` e opção `camera.format` no config (`bgr`, `rgb`, `gray`, `hsv`).

**Exemplos** (pasta `examples/`, cada um com `main.py`, `config.yaml` e `src/`)

- `cameraTracking`: a câmera acompanha um objeto vermelho movendo o pan-tilt.
- `lineDetect`: segue uma pista ou uma linha única, com controle proporcional.
- `folowCircle`: persegue uma bola vermelha com PID na posição e no tamanho.
- `lidarGraph`: gráfico em tempo real de distância, força do sinal e temperatura do Lidar.
- `lidarAvoidance`: desvia de obstáculos com o Lidar e uma máquina de estados.
- `objectDetection` (YOLOv8n) e `mediaPiper` (gestos com MediaPipe), com o extra `pip install roverlib[ai]`.
- `continuousFocus` e `slideFocus`: foco automático contínuo e foco manual pelo teclado.

**Documentação e testes**

- Site de documentação (MkDocs Material) em português: instalação, tutorial do primeiro projeto, todas as opções do `config.yaml`, arquitetura, exemplos e referência da API gerada das docstrings, com títulos traduzidos.
- README em cada plugin e módulo e um guia com o padrão de arquitetura dos plugins.
- Testes automáticos (pytest) que rodam no PC sem hardware, simulando GPIO, porta serial, câmera e I²C; os que exigem a Raspberry Pi são marcados com `@pytest.mark.hardware` e rodam com `pytest -m hardware`. São 149 testes.

### Alterado

- Todos os plugins seguem o mesmo padrão: `__init__.py` com a API pública, `exceptions.py`, indicador `HARDWARE_AVAILABLE`, versão simulada e pasta `tests/`. Os caminhos de importação antigos continuam funcionando.
- O `Robot` usa o `MotorDriver` (plugin `pin`) e cai no `VirtualMotor` fora da Raspberry Pi; aceita `simulate=` e funciona com `with`.
- Pinos padrão dos motores: direito `[17, 26]`, esquerdo `[25, 16]` (BCM).
- A máscara de `color_dual_segmentation()` tem o mesmo tamanho do frame (antes era sempre 640×640), e a função usa o `gamma` e as cores recebidos.
- `houghCircleDetect()` devolve o círculo mais votado (antes, o de maior raio) e coordenadas inteiras comuns.
- Os exemplos de foco e o `circleDetect` leem o espelhamento da câmera do config (antes era fixo no código) e usam resolução 1280×720.
- Empacotamento: licença MIT declarada, templates, documentação e fontes C++ incluídos no pacote, e dependências `pyserial`, `matplotlib`, `adafruit-blinka`, `adafruit-circuitpython-pca9685` e `adafruit-circuitpython-motor`.
- `rover_setup.sh` cria o ambiente virtual com `--system-site-packages` (para enxergar a `picamera2`) e instala `python3-dev`.

### Corrigido

- `Robot.move()` trocava os lados ao aplicar a calibração.
- `Robot.turn_degrees()` calculava a duração do giro errado (multiplicava em vez de dividir).
- `Config.get()` sem valor padrão quebrava os exemplos `lidarGraph` e `continuousFocus`; a porta do Lidar no `lidarGraph` passou a vir do config (`/dev/ttyAMA0`).
- Detecção de círculos: o Hough usava a distância mínima entre círculos (50 px) como raio mínimo, então círculos pequenos nunca eram detectados.
- `Camera.set_format()` não tinha efeito, e as conversões de cor supunham frames em RGB (eles chegam em BGR).
- `PID`: `controller_PD()` calculava P + I em vez de P + D, não atualizava o tempo entre chamadas, e a integral não aceitava valores negativos. Agora a integral fica entre `-max_I` e `max_I`, `controller_PD()` e `controller_PID()` aceitam o `dt` como argumento (útil em simulações) e `reset()` reinicia o controlador. O exemplo `lidarAvoidance`, cuja integral ficava sempre em zero, passa a usar `ki=0` para manter o comportamento.
- `autoFocus.py` não importava no PC (enums dependiam da `libcamera`).

### Removido

- Plugin `distanceSensor` (sensor ultrassônico): exige 5 V, incompatível com a lógica de 3,3 V da Raspberry Pi 5. A medição de distância é feita pelo Lidar TF-Luna.
- Driver `motor.py` baseado em `RPi.GPIO`, que não funciona na Raspberry Pi 5; substituído pelo `MotorDriver`.
- Template `templates/basic` do `rover new`, substituído pelo novo template de projeto.

Durante o desenvolvimento da 0.2.0 também foram criados e depois retirados, sem chegar a uma versão: o plugin `servoMotor` e os exemplos `servoMotor` e `servoController` (servos direto na GPIO, trocados pelo PCA9685), um driver próprio do PCA9685 (trocado pelas bibliotecas da Adafruit) e a dependência `gpiozero`.

### Para quem usava a 0.1.0

- `from roverlib.plugins.motor.motor import Motor` não existe mais: use `Robot` ou `MotorDriver` (`roverlib.plugins.motor.motorDriver`).
- `Robot.turn_degrees()` passou a girar o ângulo pedido; programas que compensavam o cálculo antigo precisam ser revistos. Os exemplos do repositório já foram ajustados.
- `CameraFormat` mudou de valores (antes eram códigos do OpenCV) e ganhou `RGB`; como `set_format()` não funcionava, nenhum programa dependia deles.
- `houghCircleDetect()` devolve `int` em vez de `numpy.uint16`.
- `PID.controller_PID()` passa a acumular erros negativos na integral: programas com `ki > 0` e erros negativos podem responder de forma diferente. Na primeira chamada, `controller_PD()` e `controller_PID()` devolvem a parcela proporcional (antes devolviam 0).
- O template do `rover new` mudou de lugar (`roverlib/cli/templates/project`).

### Pendente antes do lançamento

Itens que dependem do robô físico (detalhes em `RoverLib_Testes_2026-11-13.pdf`):

- Motores não giram por problema de hardware (bateria, ponte-H ou ligações); depois disso, validar `Robot`, calibração, template e os exemplos com rodas.
- Posição estimada do PAN imprecisa nos testes; decidir entre trocar por servo de 180° ou recalibrar.
- Validar a compilação do plugin `pin` pelo `pip install` na Raspberry Pi e o `set_format()` com a câmera real.
- Retestar o `circleDetect` com um objeto vermelho.

Para publicar: merge na `main` (o site de documentação é publicado a partir dela), versão `0.2.0` no `pyproject.toml` e envio ao PyPI **só do código-fonte (sdist)**, para que o `pip` compile o plugin `pin` na Raspberry Pi.

## [0.1.0]

Primeira versão: drivers de motor (`RPi.GPIO`), câmera (Picamera2 e webcam), Lidar e sensor ultrassônico; módulos `Robot`, `PID`, `Calibration`, `ProcessingImage` e `VisionModule`; comando `rover` (`new`, `run`, `hello`); exemplos `circleDetect`, `folowCircle`, `LidarGraph`, `roverKeypadControl`, `roverTkControl` e `slideFocus`.

[0.2.0]: https://github.com/Rover-Project/Rover/compare/main...integration/merge-branches
[0.1.0]: https://github.com/Rover-Project/Rover/tree/main
