from .src.motor import Motor # Classe que controla os motores
from .src.appControllerMotor import AppControllerMotor # Classe que cria uma interface basica de controle
from roverlib.utils.config_manager import Config
from pathlib import Path

if __name__ == "__main__":
    
    # Carrega configuração da gpio
    config = Config(Path(__file__).parent / "config.yaml")
    
    pins_motors = config.get("gpio")["motor"]
    letf = pins_motors["left"]
    right = pins_motors["right"]
    
    # Cria a instancia para controle dos motores
    motor_controller = Motor(
        left_pins=letf,
        right_pins=right,
        initial_speed=5
    )

    # Cria uma instancia para a parte grafica
    app = AppControllerMotor(motor_controller=motor_controller)

    # Executa a aplicacao
    try:
        app.run()
    except Exception as e:
        print(f"Um erro ocorreu: {e}")
        motor_controller.cleanup()
    finally:
        # Garante que o motor pare ao fechar o aplicativo
        motor_controller.cleanup()
        print("Aplicação encerrada. Motor parado.")