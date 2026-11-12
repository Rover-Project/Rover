from pathlib import Path

from src.tracker import CameraTracker


def main():
    config_path = Path(__file__).parent / "config.yaml"
    tracker = CameraTracker(config_path)

    try:
        tracker.run()
    except KeyboardInterrupt:
        print("\nExecução interrompida via terminal.")
    finally:
        tracker.cleanup()


if __name__ == "__main__":
    main()
