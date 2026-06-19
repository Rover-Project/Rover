from roverlib.modules.vision.visionModule import VisionModule
from roverlib.plugins.camera.autoFocus import AfCamera
from roverlib.plugins.camera.autoFocus import AfModeEnum
from roverlib.modules.processing.processing_image import ProcessingImage

import cv2 as openCv


def circleVoting(hough, contorno):
    if hough is None and contorno is None:
        return None

    if hough is None:
        return contorno

    if contorno is None:
        return hough

    x1, y1, r1 = hough
    x2, y2, r2 = contorno

    x1, y1, r1 = int(x1), int(y1), int(r1)
    x2, y2, r2 = int(x2), int(y2), int(r2)

    if abs(x1 - x2) < 20 and abs(y1 - y2) < 20:
        if abs(r1 - r2) < (r1 * 0.30):
            return (
                (x1 + x2) // 2,
                (y1 + y2) // 2,
                int((r1 + r2) / 2)
            )

    return contorno


def detectCircle(frame):
    mask = ProcessingImage.color_dual_segmentation(
        frame,
        gamma=1.9
    )

    hough, _ = VisionModule.houghCircleDetect(mask)
    contorno = VisionModule.circleCannyDetect(mask)

    if hough is not None and contorno is not None:
        circle = circleVoting(hough, contorno)
    elif hough is not None:
        circle = hough
    elif contorno is not None:
        circle = contorno
    else:
        circle = None

    return circle, mask


def drawCircle(frame, circle, label):
    if circle is None:
        openCv.putText(
            frame,
            f"{label}: Nenhum circulo",
            (10, 35),
            openCv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        return

    x, y, r = map(int, circle)

    openCv.circle(
        frame,
        (x, y),
        r,
        (0, 255, 0),
        3
    )

    openCv.circle(
        frame,
        (x, y),
        3,
        (0, 255, 255),
        -1
    )

    openCv.putText(
        frame,
        f"{label}: X={x} Y={y} R={r}",
        (10, 35),
        openCv.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


def smoothDetect():

    HEIGHT = 640
    WIDTH = 640

    ESP32_IP = "192.168.4.1"
    URL_STREAM = f"http://{ESP32_IP}:81/stream"

    cameraEsp = openCv.VideoCapture(URL_STREAM)

    cameraEsp.set(openCv.CAP_PROP_BUFFERSIZE, 1)
    cameraEsp.set(openCv.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cameraEsp.set(openCv.CAP_PROP_FRAME_WIDTH, WIDTH)

    cameraAf = AfCamera(
        height=HEIGHT,
        width=WIDTH,
        afMode=AfModeEnum.Continuous
    )

    cameraAf.start()

    if not cameraEsp.isOpened():
        print("Erro ao conectar na ESP32")
        return

    while True:

        _, frameEsp = cameraEsp.read()
        frameAf = cameraAf.get_frame()

        
        frameEsp = openCv.resize(
            frameEsp,
            (WIDTH, HEIGHT),
            interpolation=openCv.INTER_CUBIC
        )

        frameAf = openCv.resize(
            frameAf,
            (WIDTH, HEIGHT),
            interpolation=openCv.INTER_CUBIC
        )

        circleEsp, _ = detectCircle(frameEsp)
        circleAf, _ = detectCircle(frameAf)

        drawCircle(
            frameEsp,
            circleEsp,
            "ESP32"
        )

        drawCircle(
            frameAf,
            circleAf,
            "AF"
        )

        openCv.imshow(
            "ESP32 Camera",
            frameEsp
        )

        openCv.imshow(
            "AF Camera",
            frameAf
        )

        if openCv.waitKey(1) & 0xFF == ord('q'):
            break

    cameraEsp.release()

    try:
        cameraAf.stop()
    except:
        pass

    openCv.destroyAllWindows()


if __name__ == "__main__":
    smoothDetect()