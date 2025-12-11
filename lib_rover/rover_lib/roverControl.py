from motor import Motor # Classe que controla os motores
from control import AppControllerMotor # Classe que cria uma interface basica de controle
from constants import LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2 # pinos da GPIO dos motores

if __name__ == "__main__":
    # Cria a instancia para controle dos motores
    motor_controller = Motor(
        left_pins=(LEFT_MOTOR_1, LEFT_MOTOR_2),
        right_pins=(RIGHT_MOTOR_1, RIGHT_MOTOR_2),
        initial_speed=0.5
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