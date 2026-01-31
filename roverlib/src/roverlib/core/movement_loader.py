import importlib.metadata

def load_motor(name: str):
    eps = importlib.metadata.entry_points(group="rover.movement")
    return eps[name].load()