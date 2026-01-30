from rover.modules.movement.base import MotorDriver


class MockMotor(MotorDriver):

    def __init__(self, name):
        self.name = name

    def start(self):
        print(f"[MOCK] Motor {self.name} iniciado")

    def set(self, speed: float):
        print(f"[MOCK] Motor {self.name} velocidade: {speed}")

    def stop(self):
        print(f"[MOCK] Motor {self.name} parado")

    def cleanup(self):
        print(f"[MOCK] Motor {self.name} cleanup")
