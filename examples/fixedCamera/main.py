from roverlib.plugins.camera.camera import Camera
from pathlib import Path
from .functions import setArguments
import cv2 as openCV

HOME = Path.home()

if __name__ == "__main__":
    
    args = setArguments(
        [
            {
                "name": "h",
                "type": int,
                "help": "Altura da imagem"
            },
            
            {
                "name": "w",
                "type": int,
                "help": "Largura da imagem"
            }
        ]
    ).parse_args() 
    
    camera = Camera(args.h, args.w)
    camera.start()
    
    while(True):
        
        frame = camera.getFrame()
        
        if frame is not None:
            
            openCV.imshow(f"Frame: {args.h} x {args.w}", frame)
            
            key = openCV.waitKey(1) & 0xFF
            
            if key == ord("q"):
                break
            
    openCV.destroyAllWindows()
    camera.cleanup()