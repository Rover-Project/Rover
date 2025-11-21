from picamera2 import Picamera2
from PIL import Image
from datetime import datetime
import os

def capturar_foto_rotacionada_pil():
    picam2 = Picamera2()

    # Pasta para salvar fotos
    pasta_imagens = os.path.expanduser("~/Imagens")
    os.makedirs(pasta_imagens, exist_ok=True)

    # Gera nome automático com contador + timestamp
    contador = 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    while True:
        nome_arquivo = f"foto_{contador:04d}_{timestamp}.jpg"
        caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
        if not os.path.exists(caminho_completo):
            break
        contador += 1

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

    # Configuração da câmera
    config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(config)
    picam2.start()

    # Captura em arquivo temporário
    caminho_temp = os.path.join(pasta_imagens, "temp.jpg")
    picam2.capture_file(caminho_temp)
    picam2.stop()

    # PIL: abre, rotaciona, salva com nome final
    imagem = Image.open(caminho_temp)
    if rotacao != 0:
        imagem = imagem.rotate(-rotacao, expand=True)
    imagem.save(caminho_completo)

    os.remove(caminho_temp)

    print(f"Foto salva em: {caminho_completo}")


# Executa a função
capturar_foto_rotacionada_pil()
