import cv2
import numpy as np
import os # Importado para verificar o arquivo

# Esta função agora aceita o caminho do arquivo de imagem.
def detectar_tampa_vermelha(caminho_imagem, minDist=40, minRadius=10, maxRadius=120):
    
    # 1. CARREGAR A IMAGEM
    if not os.path.exists(caminho_imagem):
        print(f"ERRO: Arquivo não encontrado no caminho: {caminho_imagem}")
        print("Certifique-se de que o caminho está correto e o arquivo existe.")
        return

    # cv2.imread carrega a imagem em formato BGR (Azul, Verde, Vermelho)
    frame = cv2.imread(caminho_imagem)
    if frame is None:
        print("ERRO: Não foi possível carregar a imagem. Verifique se o arquivo é um formato de imagem válido.")
        return
        
    output = frame.copy() # Cria uma cópia para desenhar os resultados

    # 2. ISOLAR A COR VERMELHA (Segmentação HSV)
    # O restante do seu pipeline de processamento permanece o mesmo:

    # ... (O CÓDIGO DE SEGMENTAÇÃO HSV ABAIXO PERMANECE IGUAL) ...
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Configuração da Faixa de Vermelho (Parte 1: perto de 0 graus)
    lower_red_1 = np.array([0, 100, 100])
    upper_red_1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)

    # Configuração da Faixa de Vermelho (Parte 2: perto de 180 graus)
    lower_red_2 = np.array([160, 100, 100])
    upper_red_2 = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    # Máscara final: combina as duas faixas de vermelho
    mask = mask1 + mask2

    # Aplica a máscara para deixar visível apenas o que for vermelho
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Converte o resultado filtrado (res) para escala de cinza para o HoughCircles
    gray_masked = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    
    # Reduz o ruído na imagem filtrada
    gray_masked = cv2.medianBlur(gray_masked, 5)
    # ... (FIM DO CÓDIGO DE SEGMENTAÇÃO HSV) ...

    # 3. DETECÇÃO DE CÍRCULOS
    circles = cv2.HoughCircles(
        gray_masked,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=minDist,
        param1=100,
        param2=30,
        minRadius=minRadius,
        maxRadius=maxRadius
    )

    # 4. DESENHAR RESULTADOS
    if circles is not None:
        circles = np.uint16(np.around(circles))

        for (x, y, r) in circles[0, :]:
            # Desenha o círculo na imagem original (output)
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.circle(output, (x, y), 2, (0, 0, 255), 3)
            
            # Mostra coordenadas no frame
            cv2.putText(output, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # 5. MOSTRAR E ESPERAR
    cv2.imshow("1. Imagem Original com Deteccao", output)
    cv2.imshow("2. Imagem Filtrada (Vermelho Isolado)", res)
    
    print("Detecção concluída. Feche as janelas ou pressione qualquer tecla para continuar.")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # --- NOVO BLOCO DE INPUT ---
    
    # Solicita ao usuário que digite o caminho do arquivo
    caminho_da_imagem = input("Digite o caminho completo da imagem (Ex: foto.jpg ou /home/usuario/foto.png): ")
    
    # Remove aspas extras se o usuário as tiver colado junto com o caminho
    caminho_da_imagem = caminho_da_imagem.strip().replace('"', '').replace("'", '')
    
    detectar_tampa_vermelha(caminho_da_imagem)
    # --------------------------
