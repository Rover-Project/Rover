from pathlib import Path
from src.avoider import ObstacleAvoider

def main():
    config_path = Path(__file__).parent / "config.yaml"
    
    # Inicia o módulo passando o modo desejado ("only" ou "both")
    app = ObstacleAvoider(config_path, avoid_type="only")

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExecução interrompida via terminal.")
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()
