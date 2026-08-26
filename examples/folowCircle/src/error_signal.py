import numpy

def activation_function(error: int, thers: int =  25) -> int:
    """
    Função de ativação para o error.
    
    se o erro estiver contido dentro do intervalo [-thers, thers] retorna o próprio error caso contrário retorna 0

    Args:
        error (int): erro observado.
        thers (int, optional): limiar. Valor padrão 25.

    Returns:
        value: retorno da ativação do erro
    """
    
    return (0.0 if  numpy.abs(error) < thers else error)

def nomalize(error: float, size_interval: float) -> float:
    """
    Normaliza para o intervalo [0, size_interval]

    Args:
        error (float): erro de entrada.
        size_interval (float): intervalo de normalização

    Returns:
        float: erro normalizado para o intevalo
    """
    
    return size_interval / error

def smoothed_error(error: float, last_error: float, alph: float = 0.3) -> float:
    """
    Aplica um filtro de passas baixas no erro

    Args:
        error (float): _description_
        last_error (_type_): _description_
        alph (float, optional): _description_. Defaults to 0.3.

    Returns:
        float: _description_
    """
    
    return alph * error + (1 - alph) * last_error
            