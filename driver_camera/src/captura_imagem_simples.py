from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from datetime import datetime
import os

def capturar_foto_rotacionada():
    picam2 = Picamera2()

    # Pasta para salvar fotos
    pasta_imagens = os.path.expanduser("~/Imagens")
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)

    # Nome base
    nome_base = input("Digite o nome da foto (sem extensão): ").strip()
    if not nome_base:
        nome_base = "foto"

    # Resolução
    width = int(input("Digite a largura (pixels): "))
    height = int(input("Digite a altura (pixels): "))

    # Rotação
    while True:
        try:
            rotacao = int(input("Digite a rotação (0, 90, 180, 270): "))
            if rotacao in [0, 90, 180, 270]:
                break
            else:
                print("Digite 0, 90, 180 ou 270.")
        except ValueError:
            print("Digite um número válido.")

    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_base}_{timestamp}.jpg"
    caminho_completo = os.path.join(pasta_imagens, nome_arquivo)

    # Configuração da câmera para foto, com rotação aplicada
    config = picam2.create_still_configuration(main={"size": (width, height)}, transform=rotacao)
    picam2.configure(config)
    picam2.start()

    # Captura
    picam2.capture_file(caminho_completo)
    picam2.stop()

    print(f"Foto salva em: {caminho_completo}")


capturar_foto_rotacionada()
