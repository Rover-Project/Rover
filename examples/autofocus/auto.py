from roverlib.plugins.camera.autoFocus import AfCamera
import cv2 as openCV

if __name__ == "__main__":
    
    camera = AfCamera(height=1080, width=1080, verticalFlip=True, afMode="auto")
    camera.start()
    position = 0
    
    while True:
        
        frame = camera.getFrame()
        
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