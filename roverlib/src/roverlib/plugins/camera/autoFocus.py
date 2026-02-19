from .camera import Camera, CameraFormat
from time import sleep
from .exceptions import CameraNotStart, AutofocusModeInvalid

try: 
    # tenta importa a biblioteca libcamera, especifica da Raspbarry Pi
    from libcamera import controls # type: ignore
    availableLibcamera = True
except (ImportError, ModuleNotFoundError):
    availableLibcamera = False
    
class AfModeEnum:
    """
    Enum para guarda os valores possiveis para o modo do autofoco
    """
    Continuous = controls.AfModeEnum.Continuous
    Manual = controls.AfModeEnum.Manual 
    Auto = controls.AfModeEnum.Auto
    
class AfSpeedEnum:
    """
    Enum para guarda os valores possiveis para a velocidade do autofoco
    """
    Fast = controls.AfSpeedEnum.Fast
    Normal = controls.AfSpeedEnum.Normal
    
class AfCamera(Camera):
    """
    Extensão da classe Camera com suporte a Autofocus (AF).
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
        
        if not availableLibcamera:
            raise ModuleNotFoundError("libcamera não disponível")
        
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
            Dispara um ciclo de autofocus manual.
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
        Finaliza a ação iniciada pela run_autofocus. Colocando no modo de foco continuo
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
        Define uma posição para o foco

        Args:
            position (float): Posição de foco. valor no intervalo: [0, 1]

        Raises:
            ValueError: Dispara a exceção caso o valor esteja fora do intervalo
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
        Troca o modo de autofoco

        Args:
            mode (str): novo modo de autofoco
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
        Troca a velocidade de autofoco

        Args:
            speed (str): nova velociade de autofoco
        """
        
        self._valid()
        self.afSpeed = speed
        
        self.picam2.set_controls(
            {
                "AfSpeed": self.afSpeed # nova velocidade de autofocus
            }
        )
        
    def lock_focus(self):
        """
        Trava a posição atual de foco.
        """
        
        self._valid()
        self.set_afMode(AfModeEnum.Manual) # muda o foco para foco manual, travando posição atual
        
    def unlock_focus(self):
        """
        Destrava foco colocando no modo de foco contiuo
        """
        self._valid()
        self.set_afMode(AfModeEnum.Continuous) # moda o foco para o foco continuo
    
    def focus_time(self, duration: float = 5):
        """
        Mamtem o foco continuo durante um tempo e trava no final
        Args:
            duration (float, optional): Tempo de foco continuo. Valor padrão 5 segundos.
        """
        
        self._valid()
        self.set_afMode(AfModeEnum.Continuous) # modo foco continuo
        sleep(duration) # tempo de ajuste
        self.lock_focus() # trava a posição final de foco