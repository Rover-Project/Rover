from .src.motor import Motor # Classe que controla os motores
from .src.appControllerMotor import AppControllerMotor # Classe que cria uma interface basica de controle
from lib_rover.rover_lib.utils.config_manager import Config

if __name__ == "__main__":
    # Carrega configuração da gpio
    pins_motors = Config.get("gpio")
    letf = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))
    
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
    finally:
        # Garante que o motor pare ao fechar o aplicativo
        motor_controller.stop()
        print("Aplicação encerrada. Motor parado.")