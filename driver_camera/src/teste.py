from picamera2 import Picamera2
import time

def capturar_camera_interativa():
    picam2 = Picamera2()

    print("=== Configuração da câmera ===")
    
    # Modo
    while True:
        modo = input("Escolha o modo (foto/video): ").strip().lower()
        if modo in ['foto', 'video']:
            break
        print("Digite 'foto' ou 'video'.")

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

    # FPS
    while True:
        try:
            fps = int(input("Digite o FPS desejado (frames por segundo): "))
            if fps > 0:
                break
            else:
                print("FPS deve ser positivo.")
        except ValueError:
            print("Digite um número válido.")

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
    nome_arquivo = input("Digite o nome do arquivo (sem extensão): ").strip()
    if not nome_arquivo:
        nome_arquivo = "saida"

    # Duração (apenas para vídeo)
    duracao = 0
    if modo == "video":
        while True:
            try:
                duracao = float(input("Digite a duração do vídeo em segundos: "))
                if duracao > 0:
                    break
                else:
                    print("Digite um valor positivo.")
            except ValueError:
                print("Digite um número válido.")

    # Configuração da câmera
    config = picam2.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
    picam2.configure(config)
    picam2.rotation = rotacao
    picam2.start()

    # Captura
    if modo == "foto":
        caminho = f"{nome_arquivo}.jpg"
        picam2.capture_file(caminho)
        print(f"Foto salva em {caminho}")
    else:
        caminho = f"{nome_arquivo}.h264"
        picam2.start_recording(caminho)
        print(f"Gravando vídeo por {duracao} segundos...")
        time.sleep(duracao)
        picam2.stop_recording()
        print(f"Vídeo salvo em {caminho}")

    picam2.stop()


# Executa a função
capturar_camera_interativa()
