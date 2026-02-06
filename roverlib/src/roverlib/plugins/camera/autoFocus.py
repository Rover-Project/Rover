from .camera import Camera
from time import sleep

try: 
    # tenta importa a biblioteca libcamera, especifica da Raspbarry Pi
    from libcamera import AfModeEnum, AfSpeedEnum, AfTriggerEnum # type: ignore
    availableLibcamera = True
except (ImportError, ModuleNotFoundError):
    availableLibcamera = False
    
class AfCamera(Camera):
    """
    Extensão da classe Camera com suporte a Autofocus (AF).
    """
    
    def __init__(
        self, 
        *args, # Argumentos posicionais
        afMode: str = "continuous", 
        afSpeed: str = "normal",
        **kwargs, # Argumentos nomeados
    ):
        
        if not availableLibcamera:
            raise ModuleNotFoundError("libcamera não disponível")
        
        super().__init__(*args, **kwargs) # passa os parâmetros para a classe pai
        
        # Configuração de foco automático
        self.afMode = afMode.lower() # mode de foco
        self.afSpeed = afSpeed.lower() # velocidade de foco
        
        # método que configura o foco automático
        self._configure_autofocus()
    
    def _parse_af_mode(self) -> AfModeEnum:
        """
        Coverte a string de foco para o valor real da libcamera.

        Raises:
            ValueError: Dispara a exceção caso o tipo de foco não exista

        Returns:
            mode (int): Valor da libcamera.
        """
      
        modes = {
            "auto": AfModeEnum.Auto,
            "continuous": AfModeEnum.Continuous,
            "manual": AfModeEnum.Manual,
        } # Constantes da libcamera para tipos de foco

        if self.afMode not in modes:
            raise ValueError(f"Modo AF inválido: {self.afMode}")

        return modes[self.afMode]

    def _parse_af_speed(self) -> AfSpeedEnum:
        """
        Coverte a string de speed para o valor real da libcamera

        Raises:
            ValueError: Dispara a exceção caso a velocidade não exista

        Returns:
            speed (int): Valor da libcamera
        """
        
        speeds = {
            "slow": AfSpeedEnum.Slow,
            "normal": AfSpeedEnum.Normal,
            "fast": AfSpeedEnum.Fast,
        } # Constantes da libcamera para velocidades

        if self.afSpeed not in speeds:
            raise ValueError(f"Velocidade AF inválida: {self.afSpeed}")

        return speeds[self.afSpeed]
    
    def _configure_autofocus(self):
        """
        Configura o foco automático via libcamera.
        """

        controls = {
            "AfEnable": True,
            "AfMode": self._parse_af_mode(),
            "AfSpeed": self._parse_af_speed()
        } # Cria o controller para o libcamera

        self.picam2.set_controls(controls) # Aplica configuração de foco

    def run_autofocus(self):
        """
            Dispara um ciclo de autofocus manual.
        """
        
        if self.afMode != "auto":
            self.set_afMode("auto") # Configura o tipo de foco nescessario para a funcao
        
        self.picam2.set_controls(
            {
                "AfTrigger": AfTriggerEnum.Start
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
        
        if not 0.0 <= position <= 1.0:
            raise ValueError("LensPosition deve estar entre 0.0 e 1.0")

        self.picam2.set_controls(
            {
                "AfMode": AfModeEnum.Manual,
                "LensPosition": position
            }
        )

    def set_afMode(self, mode: str):
        """
        Troca o modo de autofoco

        Args:
            mode (str): novo modo de autofoco
        """
        
        self.afMode = mode.lower()
        
        self.picam2.set_controls(
            {
                "AfMode": self._parse_af_mode() # novo modo de autofocus
            }
        )
        
    def set_afSpeed(self, speed: str):
        """
        Troca a velocidade de autofoco

        Args:
            speed (str): nova velociade de autofoco
        """
        
        self.afSpeed = speed.lower()
        
        self.picam2.set_controls(
            {
                "AfSpeed": self._parse_af_speed() # nova velocidade de autofocus
            }
        )
        
    def lock_focus(self):
        """
        Trava a posição atual de foco.
        """
        
        self.set_afMode("manual") # muda o foco para foco manual, travando posição atual
        
    def unlock_focus(self):
        """
        Destrava foco colocando no modo de foco contiuo
        """
        
        self.set_afMode("continuous") # moda o foco para o foco continuo
        
    
    def focus_time(self, duration: float = 5):
        """
        Mamtem o foco continuo durante um tempo e trava no final
        Args:
            duration (float, optional): Tempo de foco continuo. Valor padrão 5 segundos.
        """
        
        self.set_afMode("continuous") # modo foco continuo
        sleep(duration) # tempo de ajuste
        self.lock_focus() # trava a posição final de foco