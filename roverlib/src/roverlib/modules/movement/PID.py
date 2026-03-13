import time

# Elaborar uma forma eficiente de saber os momentos (dt)
class PID:
    """
    Classe que implementa um controlador PID
    """
    
    def __init__(self, kp:float = 1, ki:float = 1, kd:float = 1, max_I: float = 100):
        self.kp = kp 
        self.ki = ki 
        self.kd = kd
        self._integral = 0
        self._last_erro = 0
        self._last_time = None
        self.max_I = max_I
    
    def controller_P(self, error: float) -> float:
        return self.kp * error
    
    def controller_PD(self, error: float) -> float:
        current_time = time.time()
        
        if self._last_time is None:
            self._last_time = current_time 
            return 0
        
        dt = current_time - self._last_time
        
        if dt <= 0:
            return 0
        
        self._integral += error * dt
        self._integral = max(0, min(self.max_I, self._integral))
        
        P = error * self.kp
        I = self._integral * self.ki 
        
        return P + I
    
    def controller_PID(self, error: float) -> float:
        
        current_time = time.time()
        
        if self._last_time is None:
            self._last_time = current_time
            self._last_erro = error
            return 0
        
        dt = current_time - self._last_time
        
        if dt <= 0:
            return 0
        
        self._integral += error * dt 
        self._integral = max(0, min(self.max_I, self._integral)) # Delimita valor para integral
        
        P = error * self.kp 
        I = self._integral * self.ki 
        D = self.kd * (error - self._last_erro) / dt
        
        # Atualiza estados
        self._last_erro = error 
        self._last_time = current_time
        
        return P + I + D
    
    def set_kp(self, kp):
        self.kp = kp 
        
    def set_ki(self, ki):
        self.ki = ki 
    
    def set_kd(self, kd):
        self.kd = kd
        
    def reset(self):
        self._integral = 0
        self._last_erro = 0
        self._last_time = time.time()