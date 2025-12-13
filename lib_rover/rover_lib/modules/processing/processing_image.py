import cv2 as openCv
import numpy

class ProcessingImage:
    """
        Modulo reposavel pelo pre-processamento de imagens, com metodos para aplicacao de filtros, segmentacao 
        entre outras ferramentas de pre-processamento
    """
    
    @classmethod 
    def ligh_adjustment(cls, img, gamma=1.9):
        """
            Realiza o ajuste do brilho de um frame deacordo com o gamma passado como parametro
        Args:
            frame (numpy array): imagem que se deseja ajustar o brilho.
            gamma (float, optional): valor de ajuste. gamma > 1: escurece o frame. gamma < 1 clareia o frame Defaults to 1.9.
        
        returns (numpy array): imagem com o brilho ajustado.
        """
        
        # tabela de correção (0–255), faz uma nova quantização das cores
        table = numpy.array([
            ((i / 255.0) ** gamma) * 255
            for i in range(256)
        ]).astype("uint8")

        # Aplica a nova quantização aos pixels do frame
        corrected = openCv.LUT(img, table)
        
        return corrected
    
    @classmethod
    def color_segmentation(cls, img, low_color1=(0, 120, 70), upper_color1=(10, 255, 255), low_color2=(170, 120, 70), upper_color2=(180, 255, 255)):
        """
            Aplica segmentacao por cor, utilizando os tons de cores passados como parametro.
            Por padrão segmenta a cor vemelha
        Args:
            frame (numpy array): Imagem que se deseja segmentar.
            low_color1 (tuple, optional): Nivel baixo da cor. Defaults to (0, 120, 70).
            upper_color1 (tuple, optional): Nivel altor da cor. Defaults to (10, 255, 255).
            low_color2 (tuple, optional): Nivel baixo da cor. Defaults to (170, 120, 70).
            upper_color2 (tuple, optional): Nivel alto da cor. Defaults to (180, 255, 255).
        
        return (numpy array): imagem com a cor segmentada.
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
            Aplica segmentacao por cor, utilizando os tons de cores passados como parametro.
            Por padrão segmenta a cor vemelha. Realiza segmentacao dupla, para diferentes niveis de brilho de acordo com o gamma passado.
        Args:
            img (_type_): _description_
            gamma (float, optional): _description_. Defaults to 2.3.
            low_color1 (tuple, optional): _description_. Defaults to (0, 120, 70).
            upper_color1 (tuple, optional): _description_. Defaults to (10, 255, 255).
            low_color2 (tuple, optional): _description_. Defaults to (170, 120, 70).
            upper_color2 (tuple, optional): _description_. Defaults to (180, 255, 255).

        Returns:
            _type_: _description_
        """
        
        frame = openCv.resize(img, (640, 640))
        
        # Aplica filtro para escurecer a imagem
        dark = ProcessingImage.ligh_adjustment(frame, 2.5)

        mask_red_dark = ProcessingImage.color_segmentation(dark) # Aplica segmentação por cor na mascara escurecida
        mask_red_normal = ProcessingImage.color_segmentation(frame) # Aplica segmentação por cor na mascara normal
        
        # Mescla as duas mascaras
        mask_final = openCv.bitwise_or(mask_red_dark, mask_red_normal)

        return mask_final
    
    @classmethod
    def edge_filter(cls, img, theres1=50, theres2=150):
        """
            Aplica filtro de bordas para uma imagem passada como parametro
        Args:
            img (_type_): _description_
            theres1 (int, optional): _description_. Defaults to 50.
            theres2 (int, optional): _description_. Defaults to 150.

        Returns:
            _type_: _description_
        """
        
        return openCv.Canny(img, theres1, theres2)