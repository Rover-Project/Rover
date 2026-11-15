"""
Aula 5 - Controlador PID discreto.

Versão didática, com o passo de tempo explícito (dt), saturação da saída e
anti-windup por limitação da integral. É usada pela simulação (sintonia.py) e
pelo controle real (seguir_objeto.py).
"""


class PID:
    """
    u = kp * e + ki * integral(e) + kd * de/dt, limitado a [-limite, limite].

    Args:
        kp, ki, kd: ganhos proporcional, integral e derivativo.
        limite: saturação da saída (no Rover, a velocidade máxima de giro).
    """

    def __init__(self, kp, ki=0.0, kd=0.0, limite=100.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.limite = limite
        self.reiniciar()

    def reiniciar(self):
        self.integral = 0.0
        self.erro_anterior = None

    def __call__(self, erro, dt):
        derivada = 0.0 if self.erro_anterior is None else (erro - self.erro_anterior) / dt
        self.erro_anterior = erro

        self.integral += erro * dt
        if self.ki:
            # anti-windup: a parcela integral sozinha nunca passa da saturação
            limite_i = self.limite / abs(self.ki)
            self.integral = max(-limite_i, min(limite_i, self.integral))

        u = self.kp * erro + self.ki * self.integral + self.kd * derivada
        return max(-self.limite, min(self.limite, u))
