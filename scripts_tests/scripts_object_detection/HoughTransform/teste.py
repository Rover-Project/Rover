import cv2
import numpy as np

# Configurações para detecção de círculos (ajustadas para olhos)
MIN_DIST = 40  # Distância mínima entre os centros dos círculos detectados
MIN_RADIUS = 15 # Raio mínimo esperado para o olho
MAX_RADIUS = 50 # Raio máximo esperado para o olho

def detectar_olhos_ao_vivo():
    # Inicializa a captura de vídeo (0 geralmente se refere à webcam padrão)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera. Verifique se ela está conectada e disponível.")
        return

    print("Iniciando detecção de olhos. Pressione 'q' para sair.")

    while True:
        # Captura quadro a quadro
        ret, frame = cap.read()
        
        if not ret:
            print("Erro ao ler o quadro. Encerrando...")
            break

        # Aumenta o tamanho do frame para melhor visualização (opcional)
        # frame = cv2.resize(frame, (640, 480))

        output = frame.copy()
        
        # 1. Pré-processamento: Converte para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. Reduz o ruído (suavização)
        gray = cv2.medianBlur(gray, 5)

        # 3. Detecção de círculos (olhos) usando HoughCircles
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=MIN_DIST,
            param1=100,  # Limiar superior para o detector Canny
            param2=30,   # Limiar de votos do centro do círculo
            minRadius=MIN_RADIUS,
            maxRadius=MAX_RADIUS
        )

        # 4. Desenhar Círculos
        if circles is not None:
            # Converte as coordenadas (x, y, r) para inteiros sem sinal de 16 bits
            circles = np.uint16(np.around(circles))

            # Itera sobre todos os círculos encontrados (se houver mais de um olho/círculo)
            for (x, y, r) in circles[0, :]:
                # Desenha o círculo na imagem original (output)
                cv2.circle(output, (x, y), r, (0, 255, 0), 2)  # Contorno
                cv2.circle(output, (x, y), 2, (0, 0, 255), 3)  # Centro
                
                # Exibe o raio e o centro
                cv2.putText(output, f"Raio: {r}", (x + 10, y - r), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


        # 5. Mostrar o resultado
        cv2.imshow('Deteccao de Olhos - Ao Vivo', output)

        # 6. Interromper o loop: Pressione 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera a câmera e fecha todas as janelas
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detectar_olhos_ao_vivo()
