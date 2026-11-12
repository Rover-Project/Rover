"""
camera_pantilt.py
==================
Teste de movimento dos servos da câmera usando o plugin diretamente.

Hardware do Rover:
  • Raspberry Pi 5 + PCA9685 no endereço 0x40 (I²C bus 1)
  • PAN  (horizontal) → canal 0, servo de ROTAÇÃO CONTÍNUA (360°): controlado por velocidade
  • TILT (vertical)   → canal 1, servo de POSIÇÃO (180°): controlado por ângulo

Em programas, prefira o PanTilt (rover.pan_tilt), que acrescenta limites,
trim, inversão de sentido e simulação no PC. Este script serve para testar
o hardware isoladamente.

Execute na Raspberry Pi:
  python camera_pantilt.py
"""
import time

from roverlib.plugins.PCAServos import PCAServos, Servo, ContinuousServo

TILT_MIN, TILT_MAX = 45, 135   # limites seguros do suporte (ajuste para o seu Rover)


def teste_pan(pan: ContinuousServo) -> None:
    """Gira o PAN para um lado e para o outro, em velocidades crescentes."""
    print("\n── PAN (servo 360°): velocidade ──")
    for velocidade in (0.2, 0.4, -0.2, -0.4):
        sentido = "direita" if velocidade > 0 else "esquerda"
        print(f"  {sentido}, velocidade {abs(velocidade):.1f} por 1 s")
        pan.throttle = velocidade
        time.sleep(1.0)
        pan.stop()
        time.sleep(0.5)
    print("  parado (se ainda girar devagar, ajuste o 'trim' do pan_tilt no config.yaml)")


def teste_tilt(tilt: Servo) -> None:
    """Varre o TILT entre os limites e volta ao centro."""
    print("\n── TILT (servo 180°): ângulo ──")
    for grau in list(range(TILT_MIN, TILT_MAX + 1, 15)) + [90]:
        tilt.angle = grau
        print(f"  TILT: {grau}°")
        time.sleep(0.4)


def main() -> None:
    print("Rover – teste dos servos da câmera (PCA9685)")

    # O 'with' garante que os sinais sejam desligados ao sair
    with PCAServos(address=0x40, frequency=50) as pca:
        pan = ContinuousServo(pca, channel=0)
        tilt = Servo(pca, channel=1, min_pulse_us=500, max_pulse_us=2500)

        pan.stop()
        tilt.center()
        time.sleep(0.5)

        teste_tilt(tilt)
        teste_pan(pan)

    print("\nTeste finalizado. Servos desligados com segurança.")


if __name__ == "__main__":
    main()
