# Plugin de Câmera

Plugin da `roverlib` responsável pela captura de imagens e vídeos do Rover. A implementação principal roda na **Raspberry Pi 5** usando a biblioteca `picamera2` (sobre o `libcamera`). Há também uma implementação simples para **webcams via OpenCV**, útil para desenvolver e testar algoritmos de visão no PC, sem o hardware do Rover.

Todas as câmeras seguem a mesma interface (`CameraInterface`), então um código de visão escrito para uma funciona com a outra, desde que use apenas os métodos comuns.

---

## Sumário

- [Estrutura](#estrutura)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Início rápido](#início-rápido)
- [Referência da API](#referência-da-api)
  - [CameraInterface](#camerainterface)
  - [Camera](#camera)
  - [AfCamera](#afcamera)
  - [Webcam](#webcam)
  - [Exceções](#exceções)
- [Exemplos](#exemplos)


---

## Estrutura

```
roverlib/plugins/camera/
├── cameraInterface.py  # Classe abstrata com o contrato comum
├── camera.py           # Camera: Picamera2/libcamera (Raspberry Pi) + enum CameraFormat
├── autofocus.py        # AfCamera: extensão com controle de autofoco + enums AfModeEnum e AfSpeedEnum
├── webcam.py           # Webcam: captura via cv2.VideoCapture
└── exceptions.py       # CameraNotStart e AutofocusModeInvalid
```

---

## Arquitetura

| Classe | Arquivo | Uso |
|--------|---------|-----|
| `CameraInterface` | `cameraInterface.py` | Classe base abstrata (`ABC`). Define os métodos obrigatórios `get_frame`, `start`, `stop` e `cleanup` |
| `Camera` | `camera.py` | Câmera da Raspberry Pi via Picamera2. Controle de exposição, brilho, contraste, saturação, FPS, corte (ROI), foto e vídeo H.264 |
| `AfCamera` | `autofocus.py` | Herda de `Camera` e adiciona controle de autofoco para módulos com lente motorizada (ex.: Camera Module 3 / IMX708, Arducam IMX519) |
| `Webcam` | `webcam.py` | Captura simples via OpenCV. Implementa só o contrato da interface |

---

## Requisitos

**Na Raspberry Pi (`Camera` e `AfCamera`)**

- Raspberry Pi OS com `libcamera` e `picamera2` (já vêm instalados nas versões recentes; senão, `sudo apt install python3-picamera2`)
- `opencv-python`
- `numpy`
- Módulo interno `roverlib.modules.processing.processing_image` (usado para o corte por ROI)
- Para `AfCamera`: um módulo de câmera com autofoco
- Para `get_picture` e `get_video`: ambiente gráfico (monitor, VNC ou X11), pois ambos abrem janelas

**No PC (`Webcam`)**

- `opencv-python`
- Uma webcam reconhecida como dispositivo `0`

Se `picamera2` ou `libcamera` não estiverem disponíveis, o construtor de `Camera` lança `ModuleNotFoundError`. Para usar a webcam automaticamente nesses casos, use `open_camera()` (veja [Exemplos](#escolhendo-a-câmera-automaticamente)).

---

## Início rápido

```python
import cv2
from roverlib.plugins.camera.camera import Camera

cam = Camera(height=480, width=640, fps=30)
cam.start()

try:
    while True:
        frame = cam.get_frame()
        cv2.imshow("Rover", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cam.cleanup()
    cv2.destroyAllWindows()
```

O ciclo de vida é sempre: **instanciar → `start()` → capturar → `cleanup()`**. Chamar métodos de captura antes do `start()` lança `CameraNotStart`.

---

## Referência da API

### CameraInterface

Contrato comum. Qualquer nova fonte de imagem (vídeo em arquivo, stream de rede etc.) deve herdar dela e implementar:

| Método | Descrição |
|--------|-----------|
| `get_frame()` | Retorna um frame como `numpy.ndarray` no formato **BGR** |
| `start()` | Inicia a captura |
| `stop()` | Interrompe a captura |
| `cleanup()` | Libera os recursos da câmera |

### Camera

```python
Camera(
    height: int,
    width: int,
    fps: int = 30,
    index: int = 0,
    format: CameraFormat | None = None,
    horizontalFlip: bool = False,
    verticalFlip: bool = False,
)
```

| Parâmetro | Descrição |
|-----------|-----------|
| `height`, `width` | Resolução dos frames |
| `fps` | Taxa de quadros |
| `index` | Índice da câmera (para placas com mais de uma câmera) |
| `format` | Conversão de cor aplicada no `get_frame` (veja [Formato dos frames](#formato-dos-frames)) |
| `horizontalFlip`, `verticalFlip` | Espelhamento feito pelo próprio ISP, sem custo de processamento |

No construtor, a câmera já é configurada com exposição automática (`AeEnable`) e balanço de branco automático (`AwbEnable`) ativados.

**Ciclo de vida**

| Método | Descrição |
|--------|-----------|
| `start()` | Inicia a câmera. Chamadas repetidas são ignoradas |
| `stop()` | Para a câmera. Pode ser reiniciada com `start()` |
| `cleanup()` | Libera os recursos (chama `stop()`) |
| `isRunning() -> bool` | Indica se a câmera está ativa |

**Ajustes de imagem**

| Método | Intervalo aceito | Descrição |
|--------|------------------|-----------|
| `set_brightness(brightness=0.0)` | `[-1.0, 1.0]` | Brilho. `0.0` é neutro |
| `set_contrast(contrast=1)` | `[0, 32]` | Contraste. `1.0` é neutro |
| `set_saturation(saturation)` | `[0, 32]` | Saturação. `1.0` é neutro, `0` gera tons de cinza |
| `set_exposure(expousure_us, gain)` | — | Desliga a exposição automática e fixa tempo de exposição (µs) e ganho analógico |
| `enable_exposure()` | — | Reativa a exposição automática |
| `set_FPS(fps)` | — | Altera a taxa de quadros |

Valores fora do intervalo lançam `ValueError`. Para visão computacional, ajustes moderados (contraste e saturação entre `1.0` e `2.0`) costumam funcionar melhor que valores extremos.

**Captura**

| Método | Descrição |
|--------|-----------|
| `get_frame()` | Retorna um frame (`numpy.ndarray`), já cortado pela ROI, se definida |
| `get_frame_time()` | Retorna a tupla `(frame, timestamp)`, com o timestamp de `time.time()` |
| `get_picture(file)` | Abre uma janela com a imagem ao vivo e salva o frame em `file` quando a tecla **`s`** é pressionada |
| `get_video(file, t)` | Grava `t` segundos de vídeo H.264 (qualidade alta) em `file`, com preview em janela |
| `metadata()` | Retorna os metadados do último frame (exposição, ganho, temperatura de cor, posição da lente etc.) |

**Região de interesse e formato**

| Método | Descrição |
|--------|-----------|
| `set_region_interest((x_start, y_start, x_end, y_end))` | Define um corte aplicado a cada `get_frame` |
| `clear_region_interest()` | Remove o corte |
| `set_format(format)` | Define a conversão de cor (`CameraFormat`) |

### AfCamera

```python
AfCamera(
    height, width, fps=30, index=0, format=None,
    horizontalFlip=False, verticalFlip=False,
    afMode: AfModeEnum = AfModeEnum.Continuous,
    afSpeed: AfSpeedEnum = AfSpeedEnum.Normal,
)
```

Aceita os mesmos parâmetros de `Camera`, mais o modo e a velocidade iniciais do autofoco, que são aplicados no `start()`. Todos os métodos abaixo exigem a câmera iniciada.

**Enums**

| Enum | Valores | Significado |
|------|---------|-------------|
| `AfModeEnum` | `Continuous` | Foca continuamente, acompanhando a cena |
| | `Auto` | Foca apenas quando um ciclo é disparado (`autofocus_cycle`) |
| | `Manual` | A lente fica parada, na posição atual ou na definida por `set_focus_position` |
| `AfSpeedEnum` | `Normal`, `Fast` | Velocidade do algoritmo de foco |

**Métodos**

| Método | Descrição |
|--------|-----------|
| `set_afMode(mode)` | Troca o modo de foco |
| `set_afSpeed(speed)` | Troca a velocidade de foco |
| `set_focus_position(position)` | Coloca em modo manual e move a lente para `position`, em **dioptrias** (veja abaixo). Valores negativos lançam `ValueError` |
| `lock_focus()` | Trava a lente na posição atual (modo `Manual`) |
| `unlock_focus()` | Volta ao foco contínuo |
| `focus_time(duration=5)` | Mantém o foco contínuo por `duration` segundos e depois trava. Bloqueia a execução durante esse tempo |
| `autofocus_cycle()` | Muda para o modo `Auto` (se necessário) e dispara um ciclo de foco único |
| `stop_autofocus_cycle()` | Cancela o ciclo em andamento. Exige o modo `Auto`, senão lança `AutofocusModeInvalid` |

**Sobre `LensPosition`:** o libcamera mede a posição da lente em dioptrias (1 / distância em metros). `0.0` foca no infinito, `1.0` a cerca de 1 m, `2.0` a 50 cm, e assim por diante. O valor máximo depende do módulo (na Camera Module 3 fica em torno de 10 a 15) e pode ser consultado em `cam.picam2.camera_controls["LensPosition"]`.

### Webcam

```python
Webcam(height, width, fps=30, index=0)
```

Usa `cv2.VideoCapture(index)`. Implementa o contrato da interface e alguns métodos comuns da `Camera`:

| Método | Descrição |
|--------|-----------|
| `get_frame()` | Retorna o frame em BGR, ou `None` se não houver frame disponível |
| `get_frame_time()` | Retorna `(frame, instante_da_captura)` |
| `isRunning()` | `True` se a webcam estiver aberta |
| `start()`, `stop()` | Sem efeito (a captura começa no construtor) |
| `cleanup()` | Libera o dispositivo |

Ajustes de ISP, ROI, foto e vídeo são exclusivos da `Camera`. Chamá-los na `Webcam` gera `AttributeError`.

### Exceções

Definidas em `exceptions.py`, ambas herdam de `RuntimeError`:

| Exceção | Quando é lançada |
|---------|------------------|
| `CameraNotStart` | Ao chamar `get_frame`, `get_frame_time`, `get_picture`, `get_video` ou os métodos de foco da `AfCamera` antes de `start()` |
| `AutofocusModeInvalid` | Ao chamar `stop_autofocus_cycle()` fora do modo `AfModeEnum.Auto` |

---

## Exemplos

### Escolhendo a câmera automaticamente

`open_camera()` usa a Picamera2 na Raspberry Pi e a webcam no PC, e já devolve a câmera iniciada:

```python
from roverlib.plugins.camera.factory import open_camera

cam = open_camera(height=480, width=640)   # Camera na RPi, Webcam no PC
frame = cam.get_frame()
cam.cleanup()
```

Use `open_camera(use_webcam=True)` para forçar a webcam, ou `use_webcam=False` para exigir a Picamera2. Opções da `Camera` (ex.: `verticalFlip=True`) podem ser passadas direto e são ignoradas na webcam.

### Ajustes de imagem e ROI

```python
from roverlib.plugins.camera.camera import Camera

cam = Camera(height=720, width=1280, fps=30, verticalFlip=True)
cam.start()

cam.set_brightness(0.1)
cam.set_contrast(1.3)
cam.set_saturation(1.2)

# Usa só a metade inferior da imagem (x_start, y_start, x_end, y_end)
cam.set_region_interest((0, 360, 1280, 720))

frame, instante = cam.get_frame_time()
print(frame.shape, instante)  # (360, 1280, 3) ...

cam.cleanup()
```

### Exposição manual

Útil em ambientes com iluminação estável, para evitar variações de brilho entre frames:

```python
cam.set_exposure(expousure_us=10000, gain=2.0)  # 10 ms, ganho 2x
# ...
cam.enable_exposure()  # volta ao automático
```

### Foto e vídeo

```python
cam = Camera(height=1080, width=1920)
cam.start()

cam.get_picture("foto.jpg")        # aperte "s" na janela para salvar
cam.get_video("video.h264", t=10)  # grava 10 segundos

cam.cleanup()
```

O vídeo é salvo como stream H.264 bruto. Para gerar um `.mp4`: `ffmpeg -i video.h264 -c copy video.mp4`.

### Autofoco

```python
from roverlib.plugins.camera.autofocus import AfCamera, AfModeEnum, AfSpeedEnum

cam = AfCamera(height=720, width=1280, afSpeed=AfSpeedEnum.Fast)
cam.start()  # começa em foco contínuo

# Deixa focar por 3 segundos e trava a lente
cam.focus_time(duration=3)

# Foco fixo a 50 cm (1 / 0.5 m = 2 dioptrias)
cam.set_focus_position(2.0)

# Ciclo de foco único sob demanda
cam.autofocus_cycle()

# Volta ao foco contínuo
cam.unlock_focus()

cam.cleanup()
```


