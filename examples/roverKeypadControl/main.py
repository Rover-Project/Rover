from pathlib import Path
from src.keypad_controller import KeypadController

def main():
    config_path = Path(__file__).parent / "config.yaml"
    controller = KeypadController(config_path)

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nExecução interrompida via terminal.")
    finally:
        # Garante que os pinos GPIO e a câmera sejam liberados
        controller.cleanup()

if __name__ == "__main__":
    main()