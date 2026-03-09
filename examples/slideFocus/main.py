from roverlib.utils.config_manager import Config
from pathlib import Path
import cv2 as openCV

if __name__ == "__main__":
    
    try:
        from roverlib.plugins.camera.autoFocus import AfCamera, AfModeEnum, AfSpeedEnum
        
        config = Config(
            Path(__file__).parent / "config.yaml"
        )
        
        cam_config = config.get("camera")
        
        camera = AfCamera(
            height=cam_config["resolution"]["h"], 
            width=cam_config["resolution"]["w"], 
            afMode=AfModeEnum.Manual, 
            afSpeed=AfSpeedEnum.Normal
        )
        camera.start()
        
        camera.set_brightness(cam_config["brigh"])
        camera.set_contrast(cam_config["contrast"])
        camera.set_saturation(cam_config["saturation"])
        
        position = 0
        
        while True:
            
            frame = camera.get_frame()
            
            if frame is not None:
                openCV.imshow("Frame", frame)

            key = openCV.waitKey(10) & 0xFF
            
            if key == ord("q"):
                break
            
            elif key == ord("w"):
                position += 1
                position = min(position, 10)
                camera.set_focus_position(position)
            elif key == ord("s"):
                position -= 1
                position = max(position, 0)
                camera.set_focus_position(position)
            

        camera.cleanup()
        openCV.destroyAllWindows()
        isAvailable = True
        
    except Exception as error:
        print(f"Error ao configura câmera com foco automático: {error}")