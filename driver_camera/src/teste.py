from picamera2 import Picamera2
from datetime import datetime
import os

def capturar_foto_unica():
    picam2 = Picamera2()

    # Pede o nome base do arquivo
    nome_base = input("Digite o nome da foto (sem extensão): ").strip()
    if not nome_base:
        nome_base = "foto"

    # Pede a pasta onde salvar (opcional)
    pasta = input("Digite a pasta para salvar (pressione Enter para usar a pasta atual): ").strip()
    if not pasta:
        pasta = os.getcwd()  # pasta atual
    else:
        if not os.path.exists(pasta):
            os.makedirs(pasta)

    # Configura a câmera com resolução padrão
    config = picam2.create_still_configuration(main={"size": (3280, 2464)})  # resolução máxima do IMX219
    picam2.configure(config)
    picam2.start()

    # Cria timestamp para o arquivo
    timestamp = datetime.now().strftime("%Y/%m/%d_%H/%M/%S")
    nome_arquivo = f"{nome_base}_{timestamp}.jpg"
    caminho_completo = os.path.join(pasta, nome_arquivo)

    # Captura a foto
    picam2.capture_file(caminho_completo)
    picam2.stop()

    print(f"Foto salva em: {caminho_completo}")


# Executa a função
capturar_foto_unica()
