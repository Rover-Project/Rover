class decision:
    def __init__(self):
        pass

    def decide(self, frame, left_line, right_line):
        if left_line is None and right_line is None:
            return "no_line"
        
        center_cam = frame.shape[1] / 2
        # Compensar a camera do video5
        calibration_offset = 47
        realCenterCam = center_cam - calibration_offset

        center_road = (left_line[1][0] + right_line[1][0]) / 2

        # calculo do erro
        erro = realCenterCam - center_road

        if erro > 0 and erro > 8:
            direcao = "Curva a Direita"
        elif erro < 0 and erro < 8:
            direcao = "Curva a Esquerda"
        else: 
            direcao = "Em frente"

        return direcao, erro

        