from picamera2 import Picamera2
from datetime import datetime
import os

def capturar_foto_documentos():
    picam2 = Picamera2()

    # Nome base do arquivo
    nome_base = input("Digite o nome da foto (sem extensão): ").strip()
    if not nome_base:
        nome_base = "foto"

    # Caminho da pasta Imagens do usuário
    pasta_imagens = os.path.expanduser("~/Imagens")
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)

    # Configura a câmera com resolução padrão (IMX219)
    config = picam2.create_still_configuration(main={"size": (3280, 2464)})
    picam2.configure(config)
    picam2.start()

    # Cria timestamp
    timestamp = datetime.now().strftime("%Y/%m/%d_%H/%M/%S")

    # Nome completo do arquivo
    nome_arquivo = f"{nome_base}_{timestamp}.jpg"
    caminho_completo = os.path.join(pasta_imagens, nome_arquivo)

    # Captura a foto
    picam2.capture_file(caminho_completo)
    picam2.stop()

    print(f"Foto salva em: {caminho_completo}")


# Executa a função
capturar_foto_documentos()


