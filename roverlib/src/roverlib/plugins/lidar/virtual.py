"""
Lidar simulado, com a mesma interface de Lidar.
Usado pelo Rover fora da Raspberry Pi (ou quando a simulação é pedida).
"""
from .exceptions import LidarNotStart

# Mesmos critérios do Lidar real
_MIN_STRENGTH = 100
_SATURATED_STRENGTH = 65535


class VirtualLidar:
    """
    Simula o Lidar TF-Luna. A distância "medida" é a que você definir:

        lidar = VirtualLidar(distance=200)
        lidar.start()
        lidar.is_obstacle(30)     # False
        lidar.set_distance(20)    # simula um obstáculo a 20 cm
        lidar.is_obstacle(30)     # True
    """

    def __init__(self, distance: float = 200, strength: int = 1000, temperature: float = 30.0,
                 verbose: bool = True, **_serial_options):
        """
        Args:
            distance: distância simulada, em cm (padrão 200 cm: caminho livre).
            strength: força do sinal simulada (abaixo de 100 a leitura é considerada inválida).
            temperature: temperatura simulada do chip, em °C.
            verbose: se True, imprime quando a distância simulada muda.
            **_serial_options: opções do Lidar real (port, baudrate...), aceitas e ignoradas.
        """
        self.verbose = verbose
        self._running = False
        self._read = (int(distance), int(strength), float(temperature))

    def _log(self, msg):
        if self.verbose:
            print(msg)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
        return False

    def start(self):
        """Inicia a simulação."""
        self._running = True
        self._log(f"[simulação] Lidar iniciado. Distância simulada: {self._read[0]} cm")

    def stop(self):
        """Encerra a simulação. Pode ser chamado mais de uma vez."""
        self._running = False

    def is_open(self):
        return self._running

    def set_distance(self, distance: float, strength: int = None):
        """Define a distância (cm) que o Lidar simulado vai informar."""
        strength = self._read[1] if strength is None else int(strength)
        if int(distance) != self._read[0]:
            self._log(f"[simulação] Lidar: distância simulada {int(distance)} cm")
        self._read = (int(distance), strength, self._read[2])

    def get_read(self):
        """Retorna (distância em cm, força do sinal, temperatura do chip)."""
        if not self._running:
            raise LidarNotStart("O Lidar simulado não foi iniciado. Chame start().")
        return self._read

    def get_distance(self, unit: str = "cm"):
        """Distância em "cm", "m" ou "mm"; None se a leitura não for confiável."""
        factors = {"cm": 1, "m": 0.01, "mm": 10}
        if unit not in factors:
            raise ValueError(f"Unidade inválida '{unit}'. Use 'cm', 'm' ou 'mm'.")
        distance, strength, _ = self.get_read()
        if distance < 0 or strength < _MIN_STRENGTH or strength == _SATURATED_STRENGTH:
            return None
        return distance * factors[unit]

    def is_obstacle(self, limit_cm: float = 30) -> bool:
        """True se houver uma leitura válida menor ou igual ao limite."""
        distance = self.get_distance("cm")
        return distance is not None and distance <= limit_cm

    def __repr__(self):
        return f"VirtualLidar(distance={self._read[0]} cm)"
