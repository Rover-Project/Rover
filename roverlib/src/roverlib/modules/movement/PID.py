import time
class PID:
    """
    Classe que implementa um controlador PID gérico para os sensores
    """
    
    def __init__(self, kp:float = 1, ki:float = 1, kd:float = 1, max_I: float = 100, max_dt: float = 0.5):
        self.kp = kp 
        self.ki = ki 
        self.kd = kd
        self._integral = 0
        self._last_erro = 0 # ultimo erro
        self._last_time = None # tempo da chamada
        self.max_I = max_I # teto para o termo integral
        self.max_dt = max_dt # teto para o termo derivada

        
    def computer(self, error: float, use_P: bool = True, use_I: bool = True, use_D: bool = True) -> float:
        """
        Calcula a resposta PID com base no erro passado como parâmetro.

        Args:
            error (float): Valor do erro atual
            use_P (bool, optional): Se deve usar a parte proporcional. Por padrão True.
            use_I (bool, optional): Se deve usar a parte integral. Por padrão True.
            use_D (bool, optional): Se deve usar a parte deriva. Por padrão True.

        Returns:
            float: amplitude da reação com base no erro passado 
        """
        
        current_time = time.time() # pega o instante de tempo atual
        
        # primeira interação 
        if self._last_time is None:
            self._last_time = current_time
            self._last_erro = error 
            return self.kp * error 
        
        dt = current_time - self._last_time # calcula a distância dos pontos ao longo do tempo
        self._last_time = current_time
        
        # em caso de erro na leitura do tempo
        if dt <= 0:
            dt = 1e-3
        
        # caso passe muito tempo desde a ultima interação
        if dt > self.max_dt:
            dt = self.max_dt 
            
        p_term = self.kp * error # termo proporcional 
        
        i_term = 0.0 # termo integral 
        if use_I and self.ki != 0:
            self._integral += error * dt # acumula o error em relacao ao ponto no tempo
            
            # considera a simetria do termo integral
            self._integral = max(
                -self.max_I, min(self.max_I, self._integral)
            )
            
            i_term = self.ki * self._integral # atribui o valor integral
            
        d_term = 0.0 # termo derivada 
        if use_D and self.kd != 0:
            d_term = (error - self._last_erro) / dt 
            d_term *= self.kd
        
        self._last_erro = error # atualiza o ultimo erro 
        
        return p_term + i_term + d_term  
    
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