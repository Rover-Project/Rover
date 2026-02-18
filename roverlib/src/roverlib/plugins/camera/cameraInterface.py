from abc import ABC, abstractmethod

class CameraInterface(ABC):
    
    @abstractmethod
    def get_frame():
        """
        Captura um único frame da câmera.

        Retorna:
            numpy.array: O frame capturado como um array NumPy no formato BGR.
        """
        pass
    
    @abstractmethod
    def start():
        """
        Inicia o funcionamento da camera.
        """
        pass
    
    @abstractmethod
    def stop():
        """
        Encerra o funcionamento da camera.
        """
        pass
    
    @abstractmethod
    def cleanup():
        """Libera os recursos da câmera."""
        pass