"""
Ponto de entrada único da RoverLib.

A classe Rover lê o config.yaml do projeto e monta os componentes configurados
(motores, câmera, Lidar, pan-tilt da câmera), usando simulação/webcam automaticamente
fora da Raspberry Pi.

Exemplo:
    from roverlib import Rover

    with Rover.from_config("config.yaml") as rover:
        rover.move.forward(50, duration=2)
        frame = rover.camera.get_frame()
        if rover.lidar.is_obstacle(30):
            rover.move.stop()
"""
from pathlib import Path

import yaml

from roverlib.modules.movement.robot import Robot
from roverlib.modules.movement.motorCalibration import Calibration


class ComponentNotAvailable(RuntimeError):
    """O componente não foi configurado ou não pôde ser iniciado."""


# Pinos padrão do Rover (mesmos usados nos exemplos)
DEFAULT_RIGHT_PINS = (17, 26)
DEFAULT_LEFT_PINS = (25, 16)

# "auto"/None no YAML significam "detectar automaticamente"
_AUTO = (None, "auto")


def _auto_bool(value):
    """Converte 'auto'/None -> None; demais valores -> bool."""
    return None if value in _AUTO else bool(value)


class Rover:
    """
    Reúne os componentes do Rover em um único objeto:

        rover.move    -> Robot (forward, backward, turn_left, turn_right, move, turn_degrees, stop)
        rover.camera  -> Camera (Raspberry Pi) ou Webcam (PC)
        rover.lidar   -> Lidar TF-Luna
        rover.pan_tilt -> PanTilt (servos da câmera: PAN 360°, TILT 180°)

    Só são criados os componentes presentes na configuração. Acessar um componente
    não configurado gera ComponentNotAvailable com a explicação do que falta.
    """

    def __init__(self, motors: dict = None, camera: dict = None, lidar: dict = None,
                 pan_tilt: dict = None):
        """
        Monta o Rover a partir de dicionários de configuração (as mesmas seções do config.yaml).
        Passe None para não usar o componente.

        Args:
            motors (dict): right, left, calibration {right, left}, pwm_frequency, simulate
            camera (dict): width, height, fps, index, webcam, horizontal_flip, vertical_flip,
                           brightness, contrast, saturation
            lidar (dict): port, baudrate, simulate, simulated_distance
            pan_tilt (dict): address, simulate, pan {channel, trim, invert, time_per_turn},
                             tilt {channel, min, max, center, invert}
        """
        self._move = None
        self._camera = None
        self._lidar = None
        self._pan_tilt = None
        self._problems = {}

        try:
            if motors is not None:
                self._move = self._build_motors(motors)
            if camera is not None:
                self._camera = self._try_build("camera", self._build_camera, camera)
            if lidar is not None:
                self._lidar = self._try_build("lidar", self._build_lidar, lidar)
            if pan_tilt is not None:
                self._pan_tilt = self._try_build("pan_tilt", self._build_pan_tilt, pan_tilt)
        except Exception:
            self.cleanup()
            raise

    # ---------- criação a partir do config.yaml ----------

    @classmethod
    def from_config(cls, path="config.yaml"):
        """
        Cria o Rover a partir de um arquivo YAML.

        Seções reconhecidas (todas opcionais):

            motors:
              right: [17, 26]
              left: [25, 16]
              calibration: {right: 1, left: 1}
              simulate: auto        # auto | true | false
            camera:
              width: 640
              height: 480
              fps: 30
              webcam: auto          # auto | true | false
            lidar:
              port: /dev/ttyAMA0
            pan_tilt:
              pan: {channel: 0}     # servo 360°
              tilt: {channel: 1}    # servo 180°

        Por compatibilidade com os exemplos, também aceita os motores em `gpio: motor:`.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: '{path}'")

        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        # Compatibilidade com os exemplos: motores em "gpio: motor:"
        if "motors" not in config and "motor" in (config.get("gpio") or {}):
            config["motors"] = config["gpio"]["motor"]

        # Seção ausente -> componente não é usado.
        # Seção vazia (ex.: "camera:") -> componente usado com valores padrão.
        def section(name):
            return (config[name] or {}) if name in config else None

        return cls(
            motors=section("motors"),
            camera=section("camera"),
            lidar=section("lidar"),
            pan_tilt=section("pan_tilt"),
        )

    # ---------- construção de cada componente ----------

    def _try_build(self, name, builder, options):
        """Componentes opcionais: se falharem, avisam e ficam indisponíveis (o programa continua)."""
        try:
            return builder(options)
        except Exception as e:
            self._problems[name] = e
            print(f"AVISO: {name} não pôde ser iniciado ({e}). rover.{name} ficará indisponível.")
            return None

    @staticmethod
    def _build_motors(options: dict) -> Robot:
        calibration = options.get("calibration") or {}
        return Robot(
            right=tuple(options.get("right", DEFAULT_RIGHT_PINS)),
            left=tuple(options.get("left", DEFAULT_LEFT_PINS)),
            calibration=Calibration(
                right=calibration.get("right", 1),
                left=calibration.get("left", 1),
            ),
            pwm_frequency=options.get("pwm_frequency", 1000),
            simulate=_auto_bool(options.get("simulate")),
        )

    @staticmethod
    def _build_camera(options: dict):
        from roverlib.plugins.camera.factory import open_camera

        cam = open_camera(
            height=options.get("height", 480),
            width=options.get("width", 640),
            fps=options.get("fps", 30),
            index=options.get("index", 0),
            use_webcam=_auto_bool(options.get("webcam")),
            horizontalFlip=bool(options.get("horizontal_flip", False)),
            verticalFlip=bool(options.get("vertical_flip", False)),
        )

        # Ajustes de imagem existem apenas na câmera da Raspberry Pi
        for key, method in (("brightness", "set_brightness"),
                            ("contrast", "set_contrast"),
                            ("saturation", "set_saturation")):
            if key in options and hasattr(cam, method):
                getattr(cam, method)(options[key])

        return cam

    @staticmethod
    def _build_lidar(options: dict):
        import os
        from roverlib.plugins.lidar import lidar as lidar_module
        from roverlib.plugins.lidar.virtual import VirtualLidar
        from roverlib.utils.simulation import resolve_simulate

        port = options.get("port", "/dev/ttyAMA0")
        hardware_available = lidar_module.availableSerial and os.path.exists(port)
        simulate = resolve_simulate(
            _auto_bool(options.get("simulate")), hardware_available,
            "Lidar", "'simulate: false' na seção lidar", simulated_name="Lidar simulado",
        )

        if simulate:
            lidar = VirtualLidar(distance=options.get("simulated_distance", 200))
        else:
            lidar = lidar_module.Lidar(port=port, baudrate=options.get("baudrate", 115200))
        lidar.start()
        return lidar

    @staticmethod
    def _build_pan_tilt(options: dict):
        from roverlib.modules.pan_tilt.pan_tilt import PanTilt

        pan = options.get("pan") or {}
        tilt = options.get("tilt") or {}
        return PanTilt(
            pan_channel=pan.get("channel", 0),
            tilt_channel=tilt.get("channel", 1),
            address=options.get("address", 0x40),
            tilt_min=tilt.get("min", 0),
            tilt_max=tilt.get("max", 180),
            tilt_center=tilt.get("center", 90),
            tilt_invert=bool(tilt.get("invert", False)),
            pan_trim=pan.get("trim", 0.0),
            pan_invert=bool(pan.get("invert", False)),
            pan_time_per_turn=pan.get("time_per_turn", 2.0),
            pan_pulse=tuple(pan.get("pulse", (500, 2500))),
            tilt_pulse=tuple(tilt.get("pulse", (500, 2500))),
            simulate=_auto_bool(options.get("simulate")),
        )

    # ---------- acesso aos componentes ----------

    def _get(self, name, value, section):
        if value is not None:
            return value
        if name in self._problems:
            raise ComponentNotAvailable(
                f"rover.{name} não está disponível: falhou ao iniciar ({self._problems[name]})."
            )
        raise ComponentNotAvailable(
            f"rover.{name} não foi configurado. Adicione a seção '{section}:' ao config.yaml."
        )

    @property
    def move(self) -> Robot:
        """Controle de movimento (Robot)."""
        return self._get("move", self._move, "motors")

    @property
    def camera(self):
        """Câmera (Camera na Raspberry Pi, Webcam no PC)."""
        return self._get("camera", self._camera, "camera")

    @property
    def lidar(self):
        """Lidar TF-Luna."""
        return self._get("lidar", self._lidar, "lidar")

    @property
    def pan_tilt(self):
        """Servos da câmera (PanTilt)."""
        return self._get("pan_tilt", self._pan_tilt, "pan_tilt")

    def has(self, name: str) -> bool:
        """Indica se um componente ('move', 'camera', 'lidar' ou 'pan_tilt') está disponível."""
        return getattr(self, f"_{name}", None) is not None

    @property
    def simulated(self) -> bool:
        """True se os motores estão em modo simulação."""
        return self._move is not None and self._move.simulated

    # ---------- encerramento ----------

    def stop(self):
        """Para os motores e o giro da câmera."""
        if self._move is not None:
            self._move.stop()
        if self._pan_tilt is not None:
            self._pan_tilt.stop()

    def cleanup(self):
        """Para os motores e libera todos os recursos. Pode ser chamado mais de uma vez."""
        for component, method in ((self._move, "cleanup"),
                                  (self._camera, "cleanup"),
                                  (self._lidar, "stop"),
                                  (self._pan_tilt, "cleanup")):
            if component is None:
                continue
            try:
                getattr(component, method)()
            except Exception as e:
                print(f"AVISO: erro ao liberar {type(component).__name__}: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def __repr__(self):
        parts = []
        if self._move is not None:
            parts.append("motores simulados" if self._move.simulated else "motores")
        if self._camera is not None:
            parts.append(type(self._camera).__name__)
        if self._lidar is not None:
            simulated = type(self._lidar).__name__ == "VirtualLidar"
            parts.append("lidar simulado" if simulated else "lidar")
        if self._pan_tilt is not None:
            parts.append("pan-tilt simulado" if self._pan_tilt.simulated else "pan-tilt")
        return f"Rover({', '.join(parts) or 'sem componentes'})"
