class Rover:
    def __init__(self, name: str):
        self.name = name

    def move(self, direction: str):
        return f"Rover {self.name} movendo para {direction}"
