import importlib.metadata

def load_cameras():
    """
    Carrega todas as implementações de câmera registradas
    no entry-point 'rover.camera'.
    """
    return {
        ep.name: ep.load()
        for ep in importlib.metadata.entry_points(group="rover.camera")
    }
