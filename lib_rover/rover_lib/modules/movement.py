"""
Módulo de movimento do Rover (compatibilidade).
Este módulo mantém compatibilidade com código antigo, mas agora usa a nova estrutura modular.
Para novos projetos, use diretamente: MovementCommands ou MovementControl
"""
import time

# Importa do novo módulo modular
try:
    from .movement import MovementCommands
except ImportError:
    try:
        # Tenta importar diretamente se o caminho relativo não funcionar
        from rover_lib.modules.movement import MovementCommands
    except ImportError:
        # Fallback se o módulo novo não estiver disponível
        MovementCommands = None

class MovementModule:
    """
    Módulo responsável pelo controle de movimento do Rover (compatibilidade).
    
    Esta classe é um wrapper que mantém compatibilidade com código antigo.
    Internamente usa MovementCommands da nova estrutura modular.
    
    Para novos projetos, considere usar MovementCommands ou MovementControl diretamente.
    """
    def __init__(self, pwm_frequency=100):
        """
        Inicializa o módulo de movimento, configura os pinos GPIO e inicia o PWM.
        
        Args:
            pwm_frequency (int): Frequência do sinal PWM em Hz (padrão: 100Hz)
        """
        if MovementCommands is None:
            raise ImportError("Módulo de movimento não disponível. Verifique a instalação.")
        
        # Usa a nova implementação modular
        self._commands = MovementCommands(pwm_frequency=pwm_frequency)
        self.pwm_frequency = pwm_frequency

    def move(self, speed_left, speed_right):
        """
        Define a velocidade e direção de ambos os motores.
        Velocidades positivas (0-100) movem para frente.
        Velocidades negativas (-100-0) movem para trás.
        
        Args:
            speed_left (float): Velocidade do motor esquerdo (-100 a 100)
            speed_right (float): Velocidade do motor direito (-100 a 100)
        """
        self._commands.move(speed_left, speed_right)

    def forward(self, speed=50):
        """
        Move o Rover para frente.
        
        Args:
            speed (float): Velocidade de 0 a 100
        """
        self._commands.forward(speed=speed)

    def backward(self, speed=50):
        """
        Move o Rover para trás.
        
        Args:
            speed (float): Velocidade de 0 a 100
        """
        self._commands.backward(speed=speed)

    def turn_left(self, speed=50):
        """
        Gira o Rover para a esquerda no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
        """
        self._commands.turn_left(speed=speed)

    def turn_right(self, speed=50):
        """
        Gira o Rover para a direita no próprio eixo.
        
        Args:
            speed (float): Velocidade de 0 a 100
        """
        self._commands.turn_right(speed=speed)

    def stop(self):
        """Para o Rover imediatamente."""
        self._commands.stop()

    def cleanup(self):
        """Limpa as configurações GPIO ao encerrar."""
        self._commands.cleanup()

# exemplo de uso
if __name__ == "__main__":
    rover_movimento = None
    try:
        rover_movimento = MovementModule()
        print("Movendo para frente por 2 segundos...")
        rover_movimento.forward(speed=60)
        time.sleep(2)

        print("Parando...")
        rover_movimento.stop()
        time.sleep(1)

        print("Virando à esquerda por 1 segundo...")
        rover_movimento.turn_left(speed=40)
        time.sleep(1)

        print("Parando...")
        rover_movimento.stop()
        time.sleep(0.5)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Garante que o cleanup seja chamado mesmo em caso de erro
        if rover_movimento:
            rover_movimento.cleanup()
