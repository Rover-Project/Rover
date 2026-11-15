from .camera import Camera
from time import sleep
from .exceptions import CameraNotStart, AutofocusModeInvalid, CameraNotAvailable
from enum import IntEnum

try:
    # tenta importa a biblioteca libcamera, especifica da Raspbarry Pi
    from libcamera import controls # type: ignore
    availableLibcamera = True
except (ImportError, ModuleNotFoundError):
    availableLibcamera = False

# Valores dos controles de foco. Na Raspberry Pi vêm do libcamera; no PC usam os
# mesmos números definidos pelo libcamera, para que o módulo continue importável.
if availableLibcamera:
    _AF_MODE = (controls.AfModeEnum.Manual, controls.AfModeEnum.Auto, controls.AfModeEnum.Continuous)
    _AF_SPEED = (controls.AfSpeedEnum.Normal, controls.AfSpeedEnum.Fast)
else:
    _AF_MODE = (0, 1, 2)
    _AF_SPEED = (0, 1)


class AfModeEnum(IntEnum):
    """Modos de foco: `Continuous` (ajusta o tempo todo), `Auto` (um ajuste por pedido) e `Manual` (posição fixa)."""
    Continuous = _AF_MODE[2]
    Manual = _AF_MODE[0]
    Auto = _AF_MODE[1]


class AfSpeedEnum(IntEnum):
    """Velocidade do autofoco: `Normal` ou `Fast`."""
    Fast = _AF_SPEED[1]
    Normal = _AF_SPEED[0]

class AfCamera(Camera):
    """
    Câmera com controle de foco, para módulos com autofoco (no Rover, a Arducam IMX519).

    Faz tudo o que a `Camera` faz e acrescenta o controle do foco. Por padrão, o foco
    é contínuo: a câmera reajusta sozinha quando a distância dos objetos muda.

    Exemplo:

    ```python
    cam = AfCamera(height=720, width=1280)
    cam.start()
    cam.focus_time(3)          # ajusta o foco por 3 s e trava
    frame = cam.get_frame()
    cam.cleanup()
    ```
    """

    def __init__(
        self,
        height:int,
        width:int,
        fps: int = 30,
        index: int = 0,
        format=None,
        horizontalFlip: bool = False,
        verticalFlip: bool = False,
        afMode: AfModeEnum = AfModeEnum.Continuous,
        afSpeed: AfSpeedEnum = AfSpeedEnum.Normal,
    ):
        """
        Args:
            height (int): altura dos frames, em pixels.
            width (int): largura dos frames, em pixels.
            fps (int): quadros por segundo. Padrão 30.
            index (int): qual câmera usar, se houver mais de uma. Padrão 0.
            format (CameraFormat, optional): conversão de cor dos frames. Padrão: nenhuma (BGR).
            horizontalFlip (bool): espelha a imagem na horizontal. Padrão False.
            verticalFlip (bool): espelha a imagem na vertical. Padrão False.
            afMode (AfModeEnum): modo de foco inicial. Padrão `Continuous`.
            afSpeed (AfSpeedEnum): velocidade do autofoco. Padrão `Normal`.

        Raises:
            CameraNotAvailable: a Picamera2 ou a libcamera não estão instaladas (por exemplo, no PC).
        """

        if not availableLibcamera:
            raise CameraNotAvailable("libcamera não disponível")

        super().__init__(
            height,
            width,
            fps,
            index,
            format,
            horizontalFlip,
            verticalFlip
        ) # passa os parâmetros para a classe pai

        # Configuração de foco automático
        self.afMode = afMode # modo do foco
        self.afSpeed = afSpeed # velocidade de foco

    def start(self):
        """Inicia a captura e aplica o modo e a velocidade de foco."""
        super().start()
        self._configure_autofocus() # método que configura o foco automático

    def _valid(self):
        """
        Valida se a câmera está ativa

        Raises:
            CameraNotStart: Dispara se a câmera não estiver ativa.
        """

        # Verifica se a camera esta ativa antes de mudar o foco
        if not self.isRunning():
            raise CameraNotStart("Você não iniciou a câmera")

    def _configure_autofocus(self):
        """
        Configura o foco automático via libcamera.
        """

        controls = {
            "AfMode": self.afMode,
            "AfSpeed": self.afSpeed
        } # Cria o controller para o libcamera

        self.picam2.set_controls(controls) # Aplica configuração de foco

    def autofocus_cycle(self):
        """
        Faz um ajuste de foco (um ciclo do autofoco) e mantém a posição encontrada.

        Coloca a câmera no modo `Auto`, se ainda não estiver.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
        """

        self._valid()
        if self.afMode != AfModeEnum.Auto:
            self.set_afMode(AfModeEnum.Auto) # Configura o tipo de foco nescessario para a funcao

        self.picam2.set_controls(
            {
                "AfTrigger": controls.AfTriggerEnum.Start
            }
        )

    def stop_autofocus_cycle(self):
        """
        Cancela um ajuste iniciado por `autofocus_cycle()`.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
            AutofocusModeInvalid: a câmera não está no modo `Auto`.
        """

        self._valid()

        if self.afMode != AfModeEnum.Auto:
            raise AutofocusModeInvalid("O método stop_autofocus exige que a câmera esteja no modo de autofocus: Auto")

        self.picam2.set_controls(
            {
                "AfTrigger":controls.AfTriggerEnum.Cancel
            }
        )

    def set_focus_position(self, position: float):
        """
        Fixa o foco em uma posição (muda para o modo `Manual`).

        Args:
            position (float): posição da lente, em dioptrias (1 / distância em metros).
                0 foca no infinito; valores maiores focam mais perto. Na IMX519 do Rover,
                o exemplo `slideFocus` usa de 0 a 10.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
            ValueError: posição negativa.
        """

        self._valid() # Valida se a camera esta ativa

        # Não permite valores negativos
        if position < 0:
            raise ValueError("A posição para o foco deve ser positiva")

        # Configura a posição do foco
        self.picam2.set_controls(
            {
                "AfMode": controls.AfModeEnum.Manual,
                "LensPosition": position
            }
        )

    def set_afMode(self, mode: AfModeEnum):
        """
        Troca o modo de foco.

        Args:
            mode (AfModeEnum): `AfModeEnum.Continuous`, `AfModeEnum.Auto` ou `AfModeEnum.Manual`.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
        """

        self._valid()
        self.afMode = mode # Atualiza o modo de foco

        self.picam2.set_controls(
            {
                "AfMode": self.afMode # novo modo de autofocus
            }
        )

    def set_afSpeed(self, speed: AfSpeedEnum):
        """
        Troca a velocidade do autofoco.

        Args:
            speed (AfSpeedEnum): `AfSpeedEnum.Normal` ou `AfSpeedEnum.Fast`.

        Raises:
            CameraNotStart: a câmera não foi iniciada com `start()`.
        """

        self._valid()
        self.afSpeed = speed

        self.picam2.set_controls(
            {
                "AfSpeed": self.afSpeed # nova velocidade de autofocus
            }
        )

    def lock_focus(self):
        """Trava o foco na posição atual (modo `Manual`)."""

        self._valid()
        self.set_afMode(AfModeEnum.Manual) # muda o foco para foco manual, travando posição atual

    def unlock_focus(self):
        """Destrava o foco, voltando ao foco contínuo."""
        self._valid()
        self.set_afMode(AfModeEnum.Continuous) # moda o foco para o foco continuo

    def focus_time(self, duration: float = 5):
        """
        Deixa o foco contínuo ajustar por um tempo e então trava a posição.

        Útil quando a cena não muda: o foco é ajustado uma vez e não "respira" depois.

        Args:
            duration (float): tempo de ajuste, em segundos. Padrão 5.
        """

        self._valid()
        self.set_afMode(AfModeEnum.Continuous) # modo foco continuo
        sleep(duration) # tempo de ajuste
        self.lock_focus() # trava a posição final de foco