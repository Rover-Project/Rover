import time


class PID:
    """
    Controlador P, PD ou PID discreto.

    A cada chamada, o controlador recebe o erro atual (referência menos medida) e
    devolve a correção:

        u = kp * e  +  ki * integral(e dt)  +  kd * de/dt

    O intervalo entre chamadas (dt) é medido com o relógio do sistema, ou pode ser
    informado (útil em simulações, que não rodam em tempo real).

    Exemplo:

    ```python
    from roverlib import PID

    pid = PID(kp=0.4, ki=0.1, kd=0.05)
    correcao = pid.controller_PID(erro)
    robot.move(speed_right=base + correcao, speed_left=base - correcao)
    ```
    """

    def __init__(self, kp: float = 1, ki: float = 1, kd: float = 1, max_I: float = 100):
        """
        Args:
            kp (float): ganho proporcional.
            ki (float): ganho integral.
            kd (float): ganho derivativo.
            max_I (float): limite do valor absoluto da integral do erro (anti-windup):
                a integral fica entre -max_I e max_I.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_I = max_I
        self._integral = 0.0
        self._last_erro = 0.0
        self._last_time = None

    def _step(self, dt):
        """
        Devolve o dt a usar e marca o instante desta chamada.

        Returns:
            float | None: o dt informado ou medido, ou None se não houver um dt válido
            (primeira chamada sem dt informado, ou dt menor ou igual a zero).
        """
        now = time.time()
        if dt is None and self._last_time is not None:
            dt = now - self._last_time
        self._last_time = now
        return dt if dt is not None and dt > 0 else None

    def controller_P(self, error: float) -> float:
        """
        Controle proporcional: `kp * erro`.

        Args:
            error (float): erro atual.

        Returns:
            float: a correção.
        """
        return self.kp * error

    def controller_PD(self, error: float, dt: float = None) -> float:
        """
        Controle proporcional-derivativo: `kp * erro + kd * d(erro)/dt`.

        Na primeira chamada (ou logo após `reset()`) ainda não há erro anterior,
        e a correção é só a parcela proporcional.

        Args:
            error (float): erro atual.
            dt (float, optional): tempo desde a chamada anterior, em segundos.
                Se omitido, é medido com o relógio do sistema.

        Returns:
            float: a correção.
        """
        first = self._last_time is None
        dt = self._step(dt)
        derivative = 0.0 if first or dt is None else (error - self._last_erro) / dt
        self._last_erro = error
        return self.kp * error + self.kd * derivative

    def controller_PID(self, error: float, dt: float = None) -> float:
        """
        Controle proporcional-integral-derivativo.

        A integral do erro fica limitada a `[-max_I, max_I]` (anti-windup). Na primeira
        chamada (ou logo após `reset()`), sem `dt` informado, a correção é só a parcela
        proporcional.

        Args:
            error (float): erro atual.
            dt (float, optional): tempo desde a chamada anterior, em segundos.
                Se omitido, é medido com o relógio do sistema.

        Returns:
            float: a correção.
        """
        first = self._last_time is None
        dt = self._step(dt)
        derivative = 0.0
        if dt is not None:
            self._integral += error * dt
            self._integral = max(-self.max_I, min(self.max_I, self._integral))
            if not first:
                derivative = (error - self._last_erro) / dt
        self._last_erro = error
        return self.kp * error + self.ki * self._integral + self.kd * derivative

    def set_kp(self, kp):
        """Troca o ganho proporcional."""
        self.kp = kp

    def set_ki(self, ki):
        """Troca o ganho integral."""
        self.ki = ki

    def set_kd(self, kd):
        """Troca o ganho derivativo."""
        self.kd = kd

    def reset(self):
        """Zera a integral e o erro anterior; a próxima chamada é tratada como a primeira."""
        self._integral = 0.0
        self._last_erro = 0.0
        self._last_time = None
