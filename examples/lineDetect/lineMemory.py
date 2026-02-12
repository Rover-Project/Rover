import numpy

class memory:
    # Quanto maior a quantidade de frames, mais suave sera a linha
    # Porem, mais lento sera o tempo de resposta
    def __init__(self, frames_number=7):
        self.frames_number = frames_number
        # ls and rs == left_side and right_side
        self.ls_memory = []
        self.rs_memory = []

    # Funcao que utiliza das ultimas linhas tracadas para gerar uma linha media
    def suavizar(self, data, side):
        memory = self.ls_memory if side == "left" else self.rs_memory

        if data is not None:
            memory.append(data)
        else:
            print("Nao ha novas linhas")

        if memory is None:
            return None

        if len(memory) > self.frames_number:
            memory.pop(0)
        
        return numpy.average(memory, axis=0)
    
