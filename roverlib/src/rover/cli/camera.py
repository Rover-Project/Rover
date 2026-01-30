import click
import cv2
from rover.core.camera_loader import load_cameras


@click.group()
def camera():
    """Comandos relacionados à câmera."""
    pass


@camera.command()
@click.option("--backend", required=True, help="Backend da câmera (webcam)")
@click.option("--width", default=640, show_default=True)
@click.option("--height", default=480, show_default=True)
@click.option("--device", default=0, show_default=True)
def test(backend, width, height, device):
    """Testa a câmera selecionada"""

    cameras = load_cameras()

    if backend not in cameras:
        click.echo(f"❌ Backend '{backend}' não encontrado.")
        click.echo(f"Disponíveis: {', '.join(cameras.keys())}")
        return

    CameraClass = cameras[backend]

    kwargs = {"width": width, "height": height}
    if backend == "webcam":
        kwargs["device"] = device

    camera = CameraClass(**kwargs)

    click.echo(f"📷 Iniciando câmera '{backend}'...")
    camera.start()

    click.echo("Pressione 'q' para sair")

    try:
        while True:
            frame = camera.read()
            frame.image = cv2.flip(frame.image, 1)

            if frame is None or frame.image is None:
                click.echo("❌ Falha ao capturar frame")
                break

            cv2.imshow("Rover Camera Test", frame.image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


    finally:
        camera.stop()
        cv2.destroyAllWindows()
        click.echo("🛑 Câmera finalizada")
