import time
import cv2
import numpy as np

try:
    # Tenta importar a biblioteca picamera2, específica da Raspberry Pi
    from picamera2 import Picamera2
except (ImportError, ModuleNotFoundError):
    print("Aviso: picamera2 não detectado. Usando mock para desenvolvimento.")
    # Mock da classe Picamera2 para desenvolvimento em outros sistemas
    class Picamera2:
        def __init__(self):
            self.is_mock = True

        def configure(self, config): pass
        def start(self): pass
        def capture_array(self, name="main"):
            # Retorna uma imagem de teste (um gradiente cinza)
            # Cria um array 3D (altura, largura, canais)
            height, width = 480, 640
            # Cria um gradiente simples para simular uma imagem
            img = np.zeros((height, width, 3), dtype=np.uint8)
            for i in range(height):
                img[i, :, 0] = int(255 * (i / height)) # Canal Azul (simulação)
                img[i, :, 1] = int(255 * (1 - (i / height))) # Canal Verde (simulação)
                img[i, :, 2] = 100 # Canal Vermelho (constante)
            return img
        def stop(self): pass

from ..utils.constants import (
    CAMERA_RESOLUTION, CAMERA_FPS, CAMERA_PREVIEW_RESOLUTION
)

class CameraModule:
    """
    Módulo para gerenciar a câmera do Rover, capturar e fornecer frames
    para o módulo de visão computacional.
    """
    def __init__(self):
        """Inicializa e configura a câmera."""
        self.picam2 = Picamera2()
        self.is_mock = hasattr(self.picam2, 'is_mock')

        if not self.is_mock:
            # Configuração real da câmera se não for o mock
            # Usamos o modo 'preview' para processamento em tempo real
            config = self.picam2.create_preview_configuration(
                main={"size": CAMERA_PREVIEW_RESOLUTION, "format": "RGB888"},
                # lores={"size": (320, 240), "format": "YUV420"}, # Stream de baixa resolução opcional
            )
            self.picam2.configure(config)
            self.picam2.start()
            print("Câmera real (picamera2) inicializada.")
        else:
            # Configuração do mock
            self.picam2.configure(None)
            self.picam2.start()
            print("Câmera mock inicializada.")

    def capture_frame(self):
        """
        Captura um único frame da câmera.

        Retorna:
            np.array: O frame capturado como um array NumPy no formato BGR.
        """
        # A picamera2 captura em formato RGB por padrão
        frame_rgb = self.picam2.capture_array("main")
        
        # Se for o mock, o frame já está em RGB (simulado)
        if self.is_mock:
            # O mock retorna um array 3D (H, W, 3) em RGB
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        else:
            # A picamera2 retorna em RGB, precisamos converter para BGR para o OpenCV
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
        return frame_bgr

    def get_preview_resolution(self):
        """Retorna a resolução de preview configurada."""
        return CAMERA_PREVIEW_RESOLUTION

    def cleanup(self):
        """Libera os recursos da câmera."""
        print("Liberando recursos da câmera...")
        self.picam2.stop()

# Exemplo de uso (para testes)
if __name__ == "__main__":
    camera = None
    try:
        camera = CameraModule()
        print(f"Resolução do preview: {camera.get_preview_resolution()}")
        print("Capturando um frame de teste...")
        
        frame = camera.capture_frame()
        
        # condicional que verifica se o frame foi capturado corretamente
        if frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
            print(f"Frame capturado com sucesso! Dimensões: {frame.shape}")
            
            cv2.imwrite("test_frame.jpg", frame) # salva o frame como uma imagem para verificação
            print("Frame de teste salvo como 'test_frame.jpg'")
        else:
            print("Falha ao capturar o frame.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        if camera:
            camera.cleanup()
