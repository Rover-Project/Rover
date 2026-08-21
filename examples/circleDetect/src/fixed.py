from roverlib.modules.vision.visionModule import VisionModule
from roverlib.modules.processing.processing_image import ProcessingImage
from roverlib.utils.config_manager import Config
from roverlib.plugins.camera.camera import Camera
from roverlib.plugins.camera.cameraInterface import CameraInterface
from pathlib import Path
from argparse import ArgumentParser, Namespace
import cv2 as openCv
import numpy

def set_args(args: list[dict]=[{"name":"", "type": None, "help": ""}], discrip:str="") -> Namespace:
    """
    Mapeia os argumentos de linha de comando passados como parâmetro.
    Args:
        args (_type_, optional): Lista de argumentos que deve ser mapeada. 
        Os dicts devem ter os seguintes campos "name", "type" e "help". 
        Valores padrões: [{"name":"", "type": None, "help": ""}].
        discrip (str, optional): Discrição dos argumentos. Por padrão "".

    Returns:
        Namespace: Objeto com os atributos parametrizados.
    """
    
    arguments = ArgumentParser(
        description=discrip 
    )

    for argument in args:
        arguments.add_argument(
            argument["name"],
            type=argument["type"],
            help=argument["help"]
        )

    return arguments.parse_args()

def voting(hough: numpy.ndarray, contour: numpy.ndarray, thers_xy: int = 20, thers_r: float = 0.3) -> numpy.ndarray:
    """
    Função de votação, para os dois métodos de detectção do círculo.

    Args:
        hough (tuple[int, int, int]): x, y e r da detecção da transformada de Hough
        contorno (tuple[int, int, int]): x, y e r  da detecção do método de contornos
        thers_xy (int, optional): Limiar de diferença para as coordenadas x e y. Por padrão 20.
        thers_r (float, optional): Limiar de diferença entre os raios. Por padrão 0.3.

    Returns:
        numpy.ndarray: Retorna uma média da coordenadas caso a discordância for menos que os limiares. Caso contrário retorna o método mais confiavel. 
    """
    
    # votação
    if abs(numpy.sum(hough[:2] - contour[:2])) < thers_xy:
        if abs(hough[2] - contour[2]) < (hough[2] * thers_r):
            return (hough + contour) // 2 

    # Se a discordancia for alta, retorna o metodo mais seguro
    return contour
    
def inInterval(v1: numpy.ndarray, v2: numpy.ndarray, thers: float) -> bool:
    """
    Verifica se a diferença de dois vetores é menor que que o limiar.

    Args:
        v1 (numpy.ndarray): Primeiro array. 
        v2 (numpy.ndarray): Segundo array.
        thers (int): limiar de diferença.

    Returns:
        bool: True se a diferença for menor que o limiar.
    """
    
    if abs(numpy.sum(v1 - v2)) > thers:
        return False
    
    return True

def cam_config(type: str="") -> CameraInterface | None:
    """
    Configura a câmera
    Args:
        type (str, optional): Tipo da câmera desejada fixa ou autofocus. Por padrão vazior que indica a webcam.
    Returns:
        cameraInterface | None: Objeto que implementa uma interface de cãmera.
    """
    
<<<<<<< HEAD:examples/circleDetect/src/circleDetect.py
    type_of_camera = set_args(
        [
            {
                "name":"camera",
                "type": str,
                "help": "O tipo de câmera que deve ser usada. Podem ser a webcam, fixa ou autofocus"
            }
        ]
    ).camera.lower()
    
    config = Config(
        Path(__file__).parent.parent / "config.yaml"
    )
    cam_config = config.get("camera")
    
    try: 
        from roverlib.plugins.camera.camera import Camera
        from roverlib.plugins.camera.autoFocus import AfCamera
    
        if type_of_camera == "autofocus":
            camera = AfCamera(
                height=cam_config["resolution"]["h"], 
                width=cam_config["resolution"]["w"], 
                fps=cam_config["fps"],
            )
        
        else:
            camera = camera = Camera(
                height=cam_config["resolution"]["h"], 
                width=cam_config["resolution"]["w"], 
                fps=cam_config["fps"],
            )
        
        camera.start()
        camera.set_brightness(cam_config["brigh"]) 
        camera.set_contrast(cam_config["contrast"])
        camera.set_saturation(cam_config["saturation"])
        
        return camera
        
    except:
        
        try:
            from roverlib.plugins.camera.webcam import Webcam    
=======
    
    camera = Camera(
        HEIGHT, 
        WIDTH, 
        fps=30,
    )
    camera.start()
    
    # Configuração base de captura
    camera.set_brightness(-0.25) # 0.5 de brilho fica muito bom
    camera.set_contrast(1)
    camera.set_saturation(1)
>>>>>>> origin/motor_refactor:examples/circleDetect/src/fixed.py

            camera = Webcam(
                height=cam_config["resolution"]["h"], 
                width=cam_config["resolution"]["w"], 
            )    
            camera.start()
            return camera
        
        except Exception as error:
            print(f"Erro na configuração da câmera: {error}")
            return None

def smoothDetect():
    circleHistory = None  # média acumulada
    LIMIAR = 20  # tolerância para considerar mesma bola
    NO_DET_LIMIT = 20  # número máximo de frames sem detecção
    noDetCounter = 0
    
    camera = cam_config()
    
    if camera is not None:
        while True:
            frame = camera.get_frame() # type: ignore
            
            if frame is not None:
                mask = ProcessingImage.color_dual_segmentation(frame, gamma=1.9)
                hough, _ = VisionModule.houghCircleDetect(mask)
                contour = VisionModule.circleCannyDetect(mask)
                
                hough = (numpy.array(hough) if hough is not None else None)
                contour = (numpy.array(contour) if contour is not None else None)

                # escolhe a melhor detecção entre hough e Canny
                if hough is not None and contour is not None:
                    det = voting(
                        hough, 
                        contour
                    )    
                elif hough is not None:
                    det = hough
                else:
                    det = contour

                if det is not None:
                    noDetCounter = 0  # reset contador de frames sem detecção

                    if circleHistory is None or not inInterval(det, circleHistory, LIMIAR):
                        circleHistory = det.copy()  # converte tupla para lista
                    else:
                        # acumula valores
                        circleHistory = (det + circleHistory) // 2 # Talves dê problema, mas vamo na fé
                        
                else:
                    noDetCounter += 1
                    # se muitos frames sem detecção, zera histórico
                    if noDetCounter >= NO_DET_LIMIT:
                        circleHistory = None

                txt = "Nenhum circulo detectado"
                if circleHistory is not None:
                    x, y, r = circleHistory
                    
                    # Desenha esferas 
                    openCv.circle(frame, (x, y), r, (0, 255, 0), 3)
                    openCv.circle(frame, (x, y), 3, (0, 255, 255), -1)
                    txt = f"X={x}  Y={y}  R={r}"

                openCv.putText(frame, txt, (10, 35), openCv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                openCv.imshow("Deteccao Final", frame)
                openCv.imshow("Mascara", mask)

                if openCv.waitKey(10) & 0xFF == ord('q'):
                    break

        camera.cleanup() # type:ignore
        openCv.destroyAllWindows()
