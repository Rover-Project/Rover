from pathlib import Path
from src.detector import LineDetectorApp

def main():
    config_path = Path(__file__).parent / "config.yaml"
    app = LineDetectorApp(config_path)

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExecução interrompida via terminal.")
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()