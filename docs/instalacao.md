# Instalação

A RoverLib roda em dois ambientes com o **mesmo código**:

| Ambiente | Motores | Câmera | Uso típico |
|---|---|---|---|
| **PC** (Windows, Linux, macOS) | simulados (comandos aparecem no terminal) | webcam | aprender, desenvolver e testar a lógica |
| **Raspberry Pi 5** no Rover | reais (GPIO + ponte-H L298N) | Picamera2 | executar no robô |

## No PC

Requer Python 3.9 ou mais recente.

```bash
python -m venv .venv
```

Ative o ambiente virtual:

=== "Windows"

    ```bash
    .venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    source .venv/bin/activate
    ```

Instale a biblioteca e confira:

```bash
pip install roverlib[cli]
rover hello
```

!!! warning "Ainda não publicada no PyPI"
    Enquanto a RoverLib não estiver no PyPI, o `pip install roverlib[cli]` não funciona. Instale a partir do repositório:

    ```bash
    git clone https://github.com/Rover-Project/Rover.git
    pip install "./Rover/roverlib[cli]"
    ```

A saída esperada é `RoverLib foi instalada corretamente.`. Siga para o [Primeiro projeto](primeiro-projeto.md).

## Na Raspberry Pi 5

### Opção 1: script de setup (recomendado)

Na raiz do repositório há o `rover_setup.sh`, que instala as dependências do sistema (incluindo `libcamera` e `rpicam-apps`), cria o ambiente virtual `.venv` e instala a RoverLib em modo de desenvolvimento:

```bash
git clone https://github.com/Rover-Project/Rover.git
cd Rover
bash rover_setup.sh
source .venv/bin/activate
```

### Opção 2: manual

```bash
sudo apt install -y python3-picamera2 python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install roverlib[cli]
```

!!! note "Por que `--system-site-packages`?"
    A `picamera2` é instalada pelo `apt` no Python do sistema. Essa opção permite que o ambiente virtual a enxergue.

### Verificando o hardware

```bash
rpicam-hello --list-cameras     # a câmera (imx519) deve aparecer na lista
python -c "from roverlib.plugins.pin import HARDWARE_AVAILABLE, gpio_base; print(HARDWARE_AVAILABLE, gpio_base())"
```

O segundo comando deve imprimir `True 571` na Raspberry Pi 5 (`True 512` na Pi 4): o módulo de GPIO foi compilado e encontrou os pinos. Se der erro ou `False`, os motores serão simulados; veja [Problemas comuns](#problemas-comuns).

### Servos da câmera (PCA9685)

Os servos do pan-tilt usam o barramento I²C. Ative-o em `sudo raspi-config` → *Interface Options* → *I2C* e confira se o PCA9685 aparece no endereço `0x40`:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

### Lidar TF-Luna (opcional)

O Lidar usa a UART da Raspberry Pi (`/dev/ttyAMA0`). Ative a porta serial em `sudo raspi-config` → *Interface Options* → *Serial Port* (shell de login: **não**; hardware serial: **sim**) e reinicie.

## Para desenvolver a biblioteca

```bash
git clone https://github.com/Rover-Project/Rover.git
cd Rover/roverlib
pip install -e .[cli,dev]
python -m pytest                 # testes do PC (sem hardware)
python -m pytest -m hardware     # na Raspberry Pi
```

Os testes que exigem a Raspberry Pi são marcados com `@pytest.mark.hardware` e só rodam com `-m hardware`.

Para visualizar esta documentação localmente:

```bash
pip install mkdocs-material "mkdocstrings[python]"
mkdocs serve
```

## Problemas comuns

**Na Raspberry Pi aparece "hardware de motores não disponível. Usando motores simulados."**
:   O módulo nativo do plugin `pin` (C++) não foi compilado. Ele é compilado automaticamente pelo `pip install` na Raspberry Pi, para a versão de Python em uso, e precisa de um compilador e dos cabeçalhos do Python. Ao importar a RoverLib aparece um aviso com o motivo. Para recompilar:

    ```bash
    sudo apt install build-essential python3-dev
    pip install -e roverlib --no-deps --force-reinstall -v
    ```

    Com `-v`, a saída mostra o resultado da compilação. Para conferir: `python -c "from roverlib.plugins.pin import HARDWARE_AVAILABLE, gpio_base; print(HARDWARE_AVAILABLE, gpio_base())"` deve mostrar `True 571` na Pi 5.

**"câmera da Raspberry Pi (picamera2) não disponível. Usando a webcam."**
:   No PC, é o comportamento esperado. Na Raspberry Pi, instale `python3-picamera2` pelo `apt` e crie o ambiente virtual com `--system-site-packages`.

**Na Raspberry Pi aparece "hardware de servos não disponível. Usando servos simulados."**
:   As bibliotecas da Adafruit não conseguiram acessar o I²C. Ative o I²C no `raspi-config` e confira a ligação do PCA9685 com `i2cdetect -y 1`.

**Quero testar o programa na Raspberry Pi sem que as rodas girem**
:   Execute com `ROVER_SIMULATE=1 rover run`. Os servos da câmera também ficam simulados.

**`rover: command not found`**
:   O ambiente virtual não está ativo, ou a biblioteca foi instalada sem o extra `[cli]`.
