from picamera2 import Picamera2
from PIL import Image
from datetime import datetime
import os

def capturar_foto_rotacionada_pil():
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

    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_base}_{timestamp}.jpg"
    caminho_completo = os.path.join(pasta_imagens, nome_arquivo)

    # Configuração da câmera
    config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(config)
    picam2.start()

    # Captura a foto
    caminho_temp = os.path.join(pasta_imagens, "temp.jpg")
    picam2.capture_file(caminho_temp)
    picam2.stop()

    # Abre a foto com PIL e aplica a rotação
    imagem = Image.open(caminho_temp)
    if rotacao != 0:
        imagem = imagem.rotate(-rotacao, expand=True)  # negativo para girar no sentido horário
    imagem.save(caminho_completo)

    # Remove arquivo temporário
    os.remove(caminho_temp)

    print(f"Foto salva em: {caminho_completo}")


# Executa a função
capturar_foto_rotacionada_pil()
