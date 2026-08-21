"""
examples/camera_pantilt.py
===========================
Exemplo de uso: Controle de câmera Pan/Tilt com dois servos.

Hardware esperado:
    • Raspberry Pi 5
    • PCA9685 no endereço padrão 0x40 (I2C bus 1)
    • Servo PAN  → canal 0  (rotação horizontal)
    • Servo TILT → canal 1  (inclinação vertical)

Para executar na Raspberry Pi:
    pip install smbus2
    python examples/camera_pantilt.py
"""

import time
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

try:
    from pca9685 import PCAServos, Servo
except ImportError as e:
    print(f"Erro ao importar pca9685: {e}")
    print("Execute: pip install smbus2")
    sys.exit(1)


def varredura_horizontal(pan: Servo, steps: int = 9) -> None:
    """Varre o servo PAN de 0° a 180° e volta ao centro."""
    print("\n── Varredura horizontal (PAN) ──")
    for grau in range(0, 181, 180 // steps):
        pan.angle = grau
        print(f"  PAN: {grau}°")
        time.sleep(0.4)
    pan.center()
    print("  PAN: 90° (centro)")


def varredura_vertical(tilt: Servo, min_grau: int = 45, max_grau: int = 135) -> None:
    """Varre o servo TILT entre os ângulos informados."""
    print("\n── Varredura vertical (TILT) ──")
    for grau in range(min_grau, max_grau + 1, 10):
        tilt.angle = grau
        print(f"  TILT: {grau}°")
        time.sleep(0.3)
    tilt.center()
    print("  TILT: 90° (centro)")


def posicao_inicial(pan: Servo, tilt: Servo) -> None:
    """Move ambos os servos para o centro."""
    print("\n── Posição inicial (centro) ──")
    pan.center()
    tilt.center()
    time.sleep(0.5)


def main() -> None:
    print("=" * 50)
    print("  Rover – Controle de Câmera Pan/Tilt")
    print("  PCA9685 Plugin próprio (sem Adafruit)")
    print("=" * 50)

    with PCAServos(address=0x40, bus=1, frequency=50) as pca:
        pan  = Servo(pca, channel=0, min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=1, min_pulse_us=600, max_pulse_us=2400)

        posicao_inicial(pan, tilt)

        print(f"\nPAN  atual: {pan.angle}°")
        print(f"TILT atual: {tilt.angle}°")

        varredura_horizontal(pan)
        time.sleep(0.5)

        varredura_vertical(tilt)
        time.sleep(0.5)

        # Aponta para canto específico
        print("\n── Posição personalizada ──")
        pan.angle  = 45
        tilt.angle = 60
        print(f"  PAN={pan.angle}°  TILT={tilt.angle}°")
        time.sleep(1.0)

        posicao_inicial(pan, tilt)

    print("\nDemo finalizado. Servos desativados.")


if __name__ == "__main__":
    main()
