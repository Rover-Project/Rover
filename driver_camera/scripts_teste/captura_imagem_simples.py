from picamera2 import Picamera2
from PIL import Image
from datetime import datetime
import os
import time

def capturar_n_fotos_rotacionadas():
    picam2 = Picamera2()

    # Pasta para salvar fotos
    pasta_imagens = os.path.expanduser("~/Imagens")
    os.makedirs(pasta_imagens, exist_ok=True)

    # ==== QUANTAS FOTOS? ====
    while True:
        try:
            n = int(input("Quantas fotos deseja tirar? "))
            if n > 0:
                break
            else:
                print("Digite um valor maior que zero.")
        except ValueError:
            print("Digite um número válido.")

    # ==== RESOLUÇÃO ====
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

    # ==== ROTAÇÃO ====
    while True:
        try:
            rotacao = int(input("Digite a rotação (0, 90, 180, 270): "))
            if rotacao in [0, 90, 180, 270]:
                break
            else:
                print("Digite 0, 90, 180 ou 270.")
        except ValueError:
            print("Digite um número válido.")

    # ==== CONFIGURA A CÂMERA UMA VEZ ====
    config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(config)
    picam2.start()

    print("\nIniciando captura de fotos...\n")

    # Gera timestamp único para todas as fotos dessa sessão
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i in range(1, n + 1):
        # Nome seguro e numerado
        prefixo = input("Digite o nome-base das fotos: ")
        nome_arquivo = f"{prefixo}_{i:04d}_{timestamp}.jpg"

        caminho_completo = os.path.join(pasta_imagens, nome_arquivo)

        # Captura temporária
        caminho_temp = os.path.join(pasta_imagens, "temp.jpg")
        picam2.capture_file(caminho_temp)

        # Abre, rotaciona e salva
        imagem = Image.open(caminho_temp)
        if rotacao != 0:
            imagem = imagem.rotate(-rotacao, expand=True)
        imagem.save(caminho_completo)

        print(f"Foto {i}/{n} salva em: {caminho_completo}")

        time.sleep(1,5)  # opcional — pausa entre capturas

    picam2.stop()
    os.remove(caminho_temp)

    print("\nCaptura finalizada com sucesso!")


# Executa a função
capturar_n_fotos_rotacionadas()
