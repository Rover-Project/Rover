import click # type: ignore
import cv2 as openCV
from roverlib.plugins.camera.picamera import  Camera
from roverlib.plugins.camera.webcam import Webcam

@click.command()
@click.option("--camera", required=True, help="Câmera que deseja usar.", type=str)
@click.option("--width", default=640, show_default=True)
@click.option("--height", default=480, show_default=True)
def camera(camera: str, width, height):
    """Uso da camera"""

    if camera.lower() == 'picamera':
        cam = Camera(width, height)

    elif camera.lower() == 'webcam':
        cam = Webcam(width, height)

    click.echo(f"Iniciando câmera '{camera}'...")
    click.echo("Pressione 'q' para sair")

    while(True):
        frame = cam.get_frame()
        
        if frame is not None:
            openCV.imshow("Camera", frame)
        
        
        key = openCV.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
    
    openCV.destroyAllWindows()
    cam.cleanup()