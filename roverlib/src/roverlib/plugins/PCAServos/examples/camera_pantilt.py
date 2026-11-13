"""
camera_pantilt.py
==================
Teste de movimento dos servos da câmera usando o plugin diretamente.
Comece com a câmera olhando para a frente do Rover.

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
TILT_CENTRO = 90               # câmera em pé

# PAN do Rover (medido): o cabo flat permite ~50° para cada lado a partir da frente.
# Com velocidade 0.2, gira ~125°/s para a direita (velocidade negativa) e
# ~100°/s para a esquerda (velocidade positiva).
PAN_GIRO = 0.2
PAN_TEMPO_DIREITA = 0.32       # ~40° para a direita
PAN_TEMPO_ESQUERDA = 0.40      # ~40° para a esquerda


def gira(pan: ContinuousServo, velocidade: float, tempo: float) -> None:
    pan.throttle = velocidade
    time.sleep(tempo)
    pan.stop()
    time.sleep(0.5)


def teste_pan(pan: ContinuousServo) -> None:
    """Gira o PAN ~40° para cada lado, sem forçar o cabo, e volta para a frente."""
    print("\n── PAN (servo 360°): velocidade ──")
    print("  direita ~40° e volta")
    gira(pan, -PAN_GIRO, PAN_TEMPO_DIREITA)
    gira(pan, PAN_GIRO, PAN_TEMPO_ESQUERDA)
    print("  esquerda ~40° e volta")
    gira(pan, PAN_GIRO, PAN_TEMPO_ESQUERDA)
    gira(pan, -PAN_GIRO, PAN_TEMPO_DIREITA)
    print("  parado de frente (se ainda girar devagar, ajuste o 'trim' do pan_tilt no config.yaml)")


def teste_tilt(tilt: Servo) -> None:
    """Varre o TILT entre os limites e volta ao centro."""
    print("\n── TILT (servo 180°): ângulo ──")
    for grau in list(range(TILT_MIN, TILT_MAX + 1, 15)) + [TILT_CENTRO]:
        tilt.angle = grau
        print(f"  TILT: {grau}°")
        time.sleep(0.4)


def main() -> None:
    print("Rover – teste dos servos da câmera (PCA9685)")

    # Comece com a câmera olhando para a frente do Rover.
    pca = PCAServos(address=0x40, frequency=50)
    pan = ContinuousServo(pca, channel=0)
    tilt = Servo(pca, channel=1, min_pulse_us=500, max_pulse_us=2500)
    try:
        pan.stop()
        tilt.angle = TILT_CENTRO
        time.sleep(0.5)

        teste_tilt(tilt)
        teste_pan(pan)
    finally:
        pan.stop()
        tilt.angle = TILT_CENTRO
        # O PAN é desligado; o TILT continua segurando a câmera em pé
        # (sem sinal, o peso da câmera a faria cair).
        pca.close(keep_channels=(1,))

    print("\nTeste finalizado. PAN desligado e TILT segurando a câmera em pé.")


if __name__ == "__main__":
    main()
