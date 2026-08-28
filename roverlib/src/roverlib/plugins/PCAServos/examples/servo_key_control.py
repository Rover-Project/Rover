import sys
import tty
import termios
from pathlib import Path
from roverlib.utils.config_manager import Config
from roverlib.plugins.PCAServos.pca9685.driver import PCA9685
from roverlib.plugins.PCAServos.pca9685.servos import ServoManager # ou a classe de servos correspondente do seu driver

# Função auxiliar para ler uma tecla sem precisar pressionar Enter (específico para Linux/Raspberry Pi)
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    # Inicializa o driver PCA9685 (endereço padrão 0x40)
    pca = PCA9685(bus_num=1, address=0x40)
    pca.set_pwm_freq(50)  # Frequência padrão para servos (50Hz)

    # Definição dos canais e LIMITES SEGUROS para proteger o cabo flat
    # Ajuste os canais (ex: canal 0 para Pan, canal 1 para Tilt) conforme a sua montagem
    PAN_CHANNEL = 0
    TILT_CHANNEL = 1

    # Limites rígidos em graus para evitar tracionar o cabo flat da câmera
    PAN_MIN, PAN_MAX = 45, 135     # Centro em 90
    TILT_MIN, TILT_MAX = 60, 120   # Centro em 90

    # Posições iniciais seguras (Centralizado)
    pan_angle = 90
    tilt_angle = 90
    step = 5

    def apply_angles():
        # Converte graus para o pulso PWM adequado do PCA9685 e envia para os canais
        # (Substitua pela chamada exata do seu driver de servos se necessário)
        pca.set_servo_angle(PAN_CHANNEL, pan_angle)
        pca.set_servo_angle(TILT_CHANNEL, tilt_angle)
        print(f"\rPan: {pan_angle}° | Tilt: {tilt_angle}°   ", end="", flush=True)

    print("=== CONTROLE MANUAL DOS SERVOS (W, A, S, D) ===")
    print("W / S: Move Tilt (Cima / Baixo)")
    print("A / D: Move Pan  (Esquerda / Direita)")
    print("Q    : Sair e centralizar com segurança\n")

    try:
        # Envia para a posição central inicial
        apply_angles()

        while True:
            key = get_key().lower()

            if key == 'q':
                print("\nSaindo...")
                break
            elif key == 'w':
                tilt_angle = min(TILT_MAX, tilt_angle + step)
            elif key == 's':
                tilt_angle = max(TILT_MIN, tilt_angle - step)
            elif key == 'd':
                pan_angle = min(PAN_MAX, pan_angle + step)
            elif key == 'a':
                pan_angle = max(PAN_MIN, pan_angle - step)
            else:
                continue

            apply_angles()

    except Exception as e:
        print(f"\nErro durante a execução: {e}")

    finally:
        # BLOCO DE SEGURANÇA: Retorna a câmera para o centro (90°) antes de fechar o programa
        print("\nRetornando para a posição central (90°)...")
        pan_angle = 90
        tilt_angle = 90
        try:
            apply_angles()
        except:
            pass
        print("Finalizado com segurança.")

if __name__ == "__main__":
    main()