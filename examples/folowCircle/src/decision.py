import numpy

def voting(hough: numpy.ndarray, contour: numpy.ndarray, thers_xy: int = 20, thers_r: float = 0.3) -> numpy.ndarray:
    """
    Função de votação, para os dois métodos de detectção do círculo.

    Args:
        hough (tuple[int, int, int]): x, y e r da detecção da transformada de Hough
        contorno (tuple[int, int, int]): x, y e r  da detecção do método de contornos
        thers_xy (int, optional): Limiar de diferença para as coordenadas x e y. Por padrão 20.
        thers_r (float, optional): Limiar de diferença entre os raios. Por padrão 0.3.

    Returns:
        numpy.ndarray: Retorna uma média da coordenadas caso a discordância for menos que os limiares. Caso contrário retorna o método mais confiavel. 
    """
    
    # votação
    if abs(numpy.sum(hough[:2] - contour[:2])) < thers_xy:
        if abs(hough[2] - contour[2]) < (hough[2] * thers_r):
            return (hough + contour) // 2 

    # Se a discordancia for alta, retorna o metodo mais seguro
    return contour
    
def inInterval(v1: numpy.ndarray, v2: numpy.ndarray, thers: float) -> bool:
    """
    Verifica se a diferença de dois vetores é menor que que o limiar.

    Args:
        v1 (numpy.ndarray): Primeiro array. 
        v2 (numpy.ndarray): Segundo array.
        thers (int): limiar de diferença.

    Returns:
        bool: True se a diferença for menor que o limiar.
    """
    
    if abs(numpy.sum(v1 - v2)) > thers:
        return False
    
    return True
