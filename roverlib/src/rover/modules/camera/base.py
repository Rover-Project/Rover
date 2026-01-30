from abc import ABC, abstractmethod
from rover.modules.camera.frame import Frame

class CameraModule(ABC):

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def read(self) -> Frame:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
