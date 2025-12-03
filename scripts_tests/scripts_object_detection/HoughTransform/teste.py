import cv2
import numpy as np
import os

def detectar_tampa_vermelha_otimizado(caminho_imagem, minDist=40, minRadius=10, maxRadius=120):
    
    if not os.path.exists(caminho_imagem):
        print(f"ERRO: Arquivo não encontrado no caminho: {caminho_imagem}")
        return

    frame = cv2.imread(caminho_imagem)
    if frame is None:
        print("ERRO: Não foi possível carregar a imagem. Verifique se o caminho ou o formato estão corretos.")
        return
        
    output = frame.copy()

    # 1. SEGMENTAÇÃO HSV OTIMIZADA PARA VERMELHO
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Faixa de Vermelho 1
    lower_red_1 = np.array([0, 80, 50])
    upper_red_1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)

    # Faixa de Vermelho 2
    lower_red_2 = np.array([160, 80, 50])
    upper_red_2 = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    mask = mask1 + mask2

    # 2. PRÉ-PROCESSAMENTO NA MÁSCARA
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    res = cv2.bitwise_and(frame, frame, mask=mask)

    gray_masked = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray_masked, 50, 150)

    # 3. DETECÇÃO DE CÍRCULOS
    circles = cv2.HoughCircles(
        edges,
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
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.circle(output, (x, y), 2, (0, 0, 255), 3)
            
            cv2.putText(output, f"({x},{y}) r={r}", (x - 40, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            print(f"Círculo detectado: Centro=({x},{y}), Raio={r}")
    else:
        print("Nenhum círculo vermelho detectado com os parâmetros atuais.")


    # 5. MOSTRAR E ESPERAR (CORRIGIDO: AGORA ESTÁ DENTRO DA FUNÇÃO)
    largura_visualizacao = 1200
    
    # Redimensiona a imagem MANTENDO A PROPORÇÃO
    output_resized = cv2.resize(
        output,
        (largura_visualizacao, int(output.shape[0] * (largura_visualizacao / output.shape[1])))
    )

    # Agora mostre a imagem redimensionada
    cv2.imshow("1. Imagem Original com Deteccao", output_resized)
    cv2.imshow("2. Mascara de Cor Aplicada (O que foi visto como Vermelho)", mask)
    cv2.imshow("3. Bordas Canny (Input para Hough)", edges)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    caminho_da_imagem = input("Digite o caminho completo da imagem (Ex: foto.jpg): ")
    caminho_da_imagem = caminho_da_imagem.strip().replace('"', '').replace("'", '')
    
    detectar_tampa_vermelha_otimizado(caminho_da_imagem)
