import time

# Elaborar uma forma eficiente de saber os momentos (dt)
class PID:
    """
    Classe que implementa um controlador PID
    """
    
    def __init__(self, kp:float = 1, ki:float = 1, kd:float = 1):
        self.kp = kp 
        self.ki = ki 
        self.kd = kd
        self._integral = 0
        self._last_erro = 0
        self._dt = 0
    
    def controller_PID(self, error: float) -> float:
        self._integral += error * self._dt 
        
        cp = error  * self.kp 
        ci = self._integral * self.ki 
        cd = self.kd * (error - self._last_erro) / self._dt
        
        self._last_erro = error # atualiza o ultimo erro
        
        return (cp + ci + cd) 
    
    def updateTime(self):
        self._dt = time.time() - self._dt
    
    def set_kp(self, kp):
        self.kp = kp 
        
    def set_ki(self, ki):
        self.ki = ki 
    
    def set_kd(self, kd):
        self.kd = kd
        
    def reset(self):
        self._integral = 0
        self._last_erro = 0
        self._dt = 0