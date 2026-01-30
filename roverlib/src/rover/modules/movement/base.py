from abc import ABC, abstractmethod

class MotorDriver(ABC):

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def set(self, speed: float): ...

    @abstractmethod
    def stop(self): ...

    @abstractmethod
    def cleanup(self): ...
