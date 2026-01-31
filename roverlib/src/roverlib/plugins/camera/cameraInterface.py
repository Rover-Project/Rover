from abc import ABC, abstractmethod

class CameraInterface(ABC):
    
    @abstractmethod
    def get_frame():
        """
        Captura um único frame da câmera.

        Retorna:
            numpy.array: O frame capturado como um array NumPy no formato BGR.
        """
        # A picamera2 captura em formato RGB por padrão
        pass
    
    @abstractmethod
    def cleanup():
        """Libera os recursos da câmera."""
        pass