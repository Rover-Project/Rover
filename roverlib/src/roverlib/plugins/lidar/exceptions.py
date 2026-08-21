class LidarNotStart(RuntimeError):
    """
    Execeção caso o Lidar não seja inicializado
    Args:
        RuntimeError (_type_): _description_
    """
    pass
class LidarDoNotRespond(RuntimeError):
    """
    Execeção caso o lidar não esteja enviando dados
    (O que aponta conexão incorreta ou falha de algum compenente)
    """
    pass