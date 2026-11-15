import cv2 as openCv
import numpy

class ProcessingImage:
    """
    Funções de pré-processamento de imagem: recorte, ajuste de brilho, segmentação por cor e bordas.

    Todas são métodos de classe: chame direto, sem criar objeto. Recebem frames em BGR
    (como os da câmera do Rover e da webcam).

    Exemplo:

    ```python
    mascara = ProcessingImage.color_segmentation(frame)   # vermelho em branco, resto em preto
    ```
    """
    
    @classmethod
    def cutImage(cls, frame, region_interest: tuple[int, int, int, int]):
        """
        Recorta uma região retangular da imagem.

        Args:
            frame (numpy.ndarray): imagem de entrada.
            region_interest (tuple[int, int, int, int]): `(x, y, largura, altura)` da região, em pixels,
                a partir do canto superior esquerdo `(x, y)`.

        Returns:
            numpy.ndarray: a região recortada.
        """
    
        x_start, y_start, x_end, y_end = region_interest
        
        return frame[y_start:y_start + y_end, x_start: x_start + x_end]
    
    @classmethod 
    def ligh_adjustment(cls, img, gamma=1.9):
        """
        Ajusta o brilho por correção gama (os tons escuros e claros mudam de forma diferente).

        Args:
            img (numpy.ndarray): imagem de entrada.
            gamma (float): maior que 1 escurece; menor que 1 clareia; 1 não muda. Padrão 1.9.

        Returns:
            numpy.ndarray: imagem com o brilho ajustado, do mesmo tamanho.
        """
        
        # tabela de correção (0–255), faz uma nova quantização das cores
        table = numpy.array([
            ((i / 255.0) ** gamma) * 255
            for i in range(256)
        ]).astype("uint8")

        # Aplica a nova quantização aos pixels do frame
        corrected = openCv.LUT(
            img, table
        )
        
        return corrected
    
    @classmethod
    def color_segmentation(cls, img, low_color1=(0, 120, 70), upper_color1=(10, 255, 255), low_color2=(170, 120, 70), upper_color2=(180, 255, 255)):
        """
        Separa os pixels de uma cor: a máscara fica branca (255) onde está a cor e preta (0) no resto.

        A imagem é convertida para HSV e filtrada por dois intervalos de cor, porque o vermelho
        fica nas duas pontas da escala de matiz (0–10 e 170–180). Depois, a máscara é limpa
        (remoção de ruído, preenchimento de buracos) e suavizada.

        Por padrão, segmenta o **vermelho**. Para outra cor, passe os intervalos HSV do OpenCV
        (matiz 0–180, saturação e valor 0–255); por exemplo, para azul use
        `low_color1=(100, 120, 70), upper_color1=(130, 255, 255)` e repita os mesmos valores no segundo par.

        Args:
            img (numpy.ndarray): imagem em BGR.
            low_color1 (tuple): limite inferior HSV do primeiro intervalo. Padrão `(0, 120, 70)`.
            upper_color1 (tuple): limite superior HSV do primeiro intervalo. Padrão `(10, 255, 255)`.
            low_color2 (tuple): limite inferior HSV do segundo intervalo. Padrão `(170, 120, 70)`.
            upper_color2 (tuple): limite superior HSV do segundo intervalo. Padrão `(180, 255, 255)`.

        Returns:
            numpy.ndarray: máscara em tons de cinza, do mesmo tamanho da imagem.
        """
        
        # Converte a escala de por par HSV
        color_hsv = openCv.cvtColor(img, openCv.COLOR_BGR2HSV)
        
        # Cria mascara com os cores passadas por parâmetro
        mask1 = openCv.inRange(color_hsv, numpy.array(low_color1), numpy.array(upper_color1))
        mask2 = openCv.inRange(color_hsv, numpy.array(low_color2), numpy.array(upper_color2))
        
        # Mecla as duas mascaras
        red_mask = openCv.bitwise_or(mask1, mask2)
        
        # limpa o ruido das mascaras
        red_mask = openCv.morphologyEx(red_mask, openCv.MORPH_OPEN, numpy.ones((5, 5), numpy.uint8))
        
        # Preenche buracos internos na mascara
        kernel_close = numpy.ones((15, 15), numpy.uint8)
        mask_close = openCv.morphologyEx(red_mask, openCv.MORPH_CLOSE, kernel_close)
        
        # preparando preenchimento de regioes por meio do floodfil
        fil = mask_close.copy()
        h, w = fil.shape[:2]
        
        # Mascara de preenchimento
        flood_mask = numpy.zeros((h + 2, w + 2), numpy.uint8)
        openCv.floodFill(fil, flood_mask, (0, 0), 255)
        fil_inv = openCv.bitwise_not(fil)
        
        # aplica floodfil na mascara
        mask_fil = mask_close | fil_inv # type: ignore
        
        # Borra imagem 
        mask_fil = openCv.GaussianBlur(mask_fil, (9, 9), 2)
        
        return mask_fil
    
    @classmethod
    def color_dual_segmentation(cls, img, gamma=2.3, low_color1=(0, 120, 70), upper_color1=(10, 255, 255), low_color2=(170, 120, 70), upper_color2=(180, 255, 255)):
        """
        Segmentação por cor mais tolerante à iluminação: combina a máscara da imagem original
        com a de uma cópia escurecida por correção gama.

        Ajuda quando o objeto tem partes muito iluminadas (reflexos), que perderiam a cor na
        imagem original. Usada pelos exemplos `circleDetect` e `folowCircle`.

        Args:
            img (numpy.ndarray): imagem em BGR.
            gamma (float): quanto escurecer a cópia (maior = mais escura). Padrão 2.3.
            low_color1 (tuple): limite inferior HSV do primeiro intervalo. Padrão `(0, 120, 70)`.
            upper_color1 (tuple): limite superior HSV do primeiro intervalo. Padrão `(10, 255, 255)`.
            low_color2 (tuple): limite inferior HSV do segundo intervalo. Padrão `(170, 120, 70)`.
            upper_color2 (tuple): limite superior HSV do segundo intervalo. Padrão `(180, 255, 255)`.

        Returns:
            numpy.ndarray: máscara do mesmo tamanho da imagem (branco = cor encontrada).
        """
        
        # A máscara tem o mesmo tamanho da imagem recebida, para as coordenadas baterem com o frame
        frame = img

        # Aplica filtro para escurecer a imagem (gamma > 1 escurece)
        dark = ProcessingImage.ligh_adjustment(frame, gamma)

        colors = (low_color1, upper_color1, low_color2, upper_color2)
        mask_red_dark = ProcessingImage.color_segmentation(dark, *colors) # Aplica segmentação por cor na mascara escurecida
        mask_red_normal = ProcessingImage.color_segmentation(frame, *colors) # Aplica segmentação por cor na mascara normal
        
        # Mescla as duas mascaras
        mask_final = openCv.bitwise_or(mask_red_dark, mask_red_normal)

        return mask_final
    
    @classmethod
    def edge_filter(cls, img, theres1=50, theres2=150):
        """
        Detecta bordas com o filtro de Canny.

        Args:
            img (numpy.ndarray): imagem (em tons de cinza ou máscara).
            theres1 (int): limiar inferior: bordas mais fracas que isso são descartadas. Padrão 50.
            theres2 (int): limiar superior: bordas mais fortes que isso são sempre mantidas. Padrão 150.

        Returns:
            numpy.ndarray: imagem binária com as bordas em branco.
        """
        
        return openCv.Canny(img, theres1, theres2)