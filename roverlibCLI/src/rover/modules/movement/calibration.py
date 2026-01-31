class MotorCalibration:

    def __init__(self, left=1.0, right=1.0):
        self.left = left
        self.right = right

    def apply(self, l, r):
        return l * self.left, r * self.right
