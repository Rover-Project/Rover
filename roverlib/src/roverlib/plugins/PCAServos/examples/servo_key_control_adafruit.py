import sys
import tty
import termios
import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def get_key():
    """Lê uma tecla do terminal sem precisar pressionar Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    # Limites rígidos de segurança para proteger o cabo flat da câmera
    PAN_MIN, PAN_MAX = 45, 135     # Centro é 90
    TILT_MIN, TILT_MAX = 60, 120   # Centro é 90
    STEP = 5                       # Graus por toque
    
    print("Inicializando comunicação I2C com Adafruit PCA9685...")
    
    try:
        # Inicializa o barramento I2C e a placa PCA9685
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c, address=0x40)
        pca.frequency = 50
        
        # Cria os objetos dos servos nos canais 0 e 1
        pan_servo = servo.Servo(pca.channels[0])
        tilt_servo = servo.Servo(pca.channels[1])
        
        # Centraliza inicialmente
        pan_angle = 90
        tilt_angle = 90
        pan_servo.angle = pan_angle
        tilt_servo.angle = tilt_angle
        
        print("\n=== CONTROLE MANUAL PAN/TILT (ADAFRUIT) ===")
        print(" W / S : Tilt (Cima / Baixo)")
        print(" A / D : Pan  (Esquerda / Direita)")
        print(" C     : Recentralizar a câmera")
        print(" Q     : Sair e desativar torque\n")
        
        while True:
            key = get_key().lower()
            
            if key == 'q':
                break
            elif key == 'c':
                pan_angle = 90
                tilt_angle = 90
            elif key == 'w':
                tilt_angle = max(TILT_MIN, tilt_angle - STEP)
            elif key == 's':
                tilt_angle = min(TILT_MAX, tilt_angle + STEP)
            elif key == 'a':
                pan_angle = max(PAN_MIN, pan_angle - STEP)
            elif key == 'd':
                pan_angle = min(PAN_MAX, pan_angle + STEP)
            
            # Aplica o ângulo usando a biblioteca Adafruit
            pan_servo.angle = pan_angle
            tilt_servo.angle = tilt_angle
            
            print(f"\rPosição atual -> Pan: {pan_angle:03d}° | Tilt: {tilt_angle:03d}°   ", end="", flush=True)

    except Exception as e:
        print(f"\nErro de execução: {e}")
        
    finally:
        print("\n\nEncerrando: centralizando a câmera e cortando o torque para proteger o cabo...")
        try:
            # Retorna para o meio
            pan_servo.angle = 90
            tilt_servo.angle = 90
            time.sleep(0.5) # Aguarda meio segundo para o movimento mecânico terminar
            
            # Na biblioteca Adafruit, setar 'fraction' como None desliga o PWM do canal
            pan_servo.fraction = None
            tilt_servo.fraction = None
            
            # Libera os recursos do I2C
            pca.deinit()
        except Exception:
            pass
        print("Sistema desligado com segurança.")

if __name__ == "__main__":
    main()