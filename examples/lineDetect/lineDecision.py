class decision:
    def __init__(self, speed):
        base_speed = speed

    def decide(self, frame, left_line, right_line):
        if left_line is None and right_line is None:
            return "parar"
        
        center_cam = frame.shape[1] / 2

        center_road = (left_line[1][0] + right_line[1][0]) / 2

        # calculo do erro
        erro = center_cam - center_road

        if erro > 0 and erro > 8:
            direcao = "Direita"

        elif erro < 0 and erro < 8:
            direcao = "Esquerda"

        else: 
            direcao = "Frente"

        return direcao, erro