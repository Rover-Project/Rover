from picamera2 import Picamera2
from datetime import datetime
import os

def capturar_foto():
    picam2 = Picamera2()

    print("=== Configuração da câmera ===")

    # Resolução
    while True:
        try:
            width = int(input("Digite a largura (pixels): "))
            height = int(input("Digite a altura (pixels): "))
            if width > 0 and height > 0:
                break
            else:
                print("Valores devem ser positivos.")
        except ValueError:
            print("Digite números válidos.")

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

    # Nome do arquivo
    nome_base = input("Digite o nome da foto (sem extensão): ").strip()
    if not nome_base:
        nome_base = "foto"

    # Caminho da pasta Imagens do usuário
    pasta_imagens = os.path.expanduser("~/Imagens")
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)

    # Adiciona timestamp para garantir nome único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_base}_{timestamp}.jpg"
    caminho_completo = os.path.join(pasta_imagens, nome_arquivo)

    # Configuração da câmera
    config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(config)
    picam2.rotation = rotacao
    picam2.start()

    # Captura a foto
    picam2.capture_file(caminho_completo)
    picam2.stop()

    print(f"Foto salva em: {caminho_completo}")


# Executa a função
capturar_foto()
