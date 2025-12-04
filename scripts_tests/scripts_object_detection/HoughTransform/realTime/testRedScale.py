from picamera2 import Picamera2
import cv2
import numpy as np
import time

def main(h=680, w=480):
    picam = Picamera2()

    config = picam.create_preview_configuration(
        main={"format": "RGB888", "size": (h, w)}
    )
    picam.configure(config)
    picam.start()
    time.sleep(1)

    print("\n=== VISUALIZADOR HSV ===")
    print("→ Aponte a bola vermelha para o centro da imagem.")
    print("→ Os valores HSV do pixel central aparecerão no console.")
    print("→ Pressione Q para sair.\n")

    # Limites iniciais (ajustados, mas você vai calibrar)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    while True:
        frame = picam.capture_array()

        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        # Pixel central
        cx, cy = w // 2, h // 2
        hsv_center = hsv[cy, cx]

        print("HSV centro:", hsv_center)

        # Máscara vermelha
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Mostrar um quadradinho no centro
        cv2.rectangle(frame, (cx - 10, cy - 10), (cx + 10, cy + 10), (0, 255, 0), 1)

        cv2.imshow("Imagem Original", frame)
        cv2.imshow("Mascara Vermelha", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
