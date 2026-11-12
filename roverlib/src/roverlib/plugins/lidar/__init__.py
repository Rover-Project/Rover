"""
Plugin lidar: sensor de distância Lidar TF-Luna (UART).

    from roverlib.plugins.lidar import Lidar, VirtualLidar, HARDWARE_AVAILABLE

Pelo Rover, é acessado como rover.lidar (simulado automaticamente fora da Raspberry Pi).
"""
from .lidar import Lidar, HARDWARE_AVAILABLE
from .virtual import VirtualLidar
from .exceptions import LidarNotStart, LidarDoNotRespond, LidarNotAvailable

__all__ = [
    "Lidar", "VirtualLidar", "HARDWARE_AVAILABLE",
    "LidarNotStart", "LidarDoNotRespond", "LidarNotAvailable",
]
