import sys
import tty
import termios
import time
from roverlib.plugins.PCAServos.pca9685.servos import PCAServos, Servo

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
    
    print("Inicializando comunicação com PCA9685...")
    
    try:
        # Instancia a interface principal usando a sua classe
        pca = PCAServos(address=0x40, bus=1, frequency=50)
        
        # Cria os objetos dos servos (ajuste os canais se a montagem for diferente)
        pan_servo = Servo(pca, channel=0)
        tilt_servo = Servo(pca, channel=1)
        
        # Centraliza inicialmente
        pan_servo.center()
        tilt_servo.center()
        
        pan_angle = 90
        tilt_angle = 90
        
        print("\n=== CONTROLE MANUAL PAN/TILT (CABO FLAT SEGURO) ===")
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
                # Subtrai ou soma dependendo de como o servo foi montado fisicamente no suporte
                tilt_angle = max(TILT_MIN, tilt_angle - STEP)
            elif key == 's':
                tilt_angle = min(TILT_MAX, tilt_angle + STEP)
            elif key == 'a':
                pan_angle = max(PAN_MIN, pan_angle - STEP)
            elif key == 'd':
                pan_angle = min(PAN_MAX, pan_angle + STEP)
            
            # Aplica o ângulo usando a sua propriedade @angle.setter
            pan_servo.angle = pan_angle
            tilt_servo.angle = tilt_angle
            
            print(f"\rPosição atual -> Pan: {pan_angle:03d}° | Tilt: {tilt_angle:03d}°   ", end="", flush=True)

    except Exception as e:
        print(f"\nErro de execução: {e}")
        
    finally:
        print("\n\nEncerrando: centralizando a câmera e cortando o torque para proteger o cabo...")
        try:
            # Retorna para o meio
            pan_servo.center()
            tilt_servo.center()
            time.sleep(0.5) # Aguarda meio segundo para o movimento mecânico terminar
            
            # Libera o motor para não forçar o cabo desligado
            pan_servo.detach()
            tilt_servo.detach()
            
            # Fecha o barramento I2C
            pca.close()
        except Exception:
            pass
        print("Sistema desligado com segurança.")

if __name__ == "__main__":
    main()
