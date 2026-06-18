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


# ---------------------------------------------------------------------------
# Parâmetros de velocidade segura
# ---------------------------------------------------------------------------
# Passo angular por iteração: quanto menor, mais suave e seguro o movimento.
# 1° por passo é bastante conservador — bom para evitar solavancos.
PASSO_GRAUS   = 1       # graus por passo
DELAY_PASSO   = 0.02    # segundos entre cada passo (20 ms → ~50°/s)
DELAY_DESTINO = 0.4     # pausa ao chegar em cada posição de varredura


# ---------------------------------------------------------------------------
# Movimento suave — função central de segurança
# ---------------------------------------------------------------------------
def mover_suave(servo: Servo, destino: float,
                passo: float = PASSO_GRAUS,
                delay: float = DELAY_PASSO) -> None:
    """
    Move um servo do ângulo atual até o destino de forma gradual,
    incrementando 'passo' graus por vez com 'delay' segundos de espera
    entre cada incremento.

    Isso evita solavancos, reduz a corrente de pico no servo e protege
    o mecanismo de pan/tilt contra impactos mecânicos bruscos.

    Parâmetros
    ----------
    servo   : Servo  – instância do servo a mover
    destino : float  – ângulo final desejado (graus)
    passo   : float  – incremento por iteração (padrão: 1°)
    delay   : float  – espera entre passos em segundos (padrão: 0.02 s)
    """
    origem = servo.angle if servo.angle is not None else 90.0
    destino = float(destino)

    if abs(destino - origem) < 0.5:
        return   # já está no destino, não precisa mover

    direcao = 1.0 if destino > origem else -1.0
    angulo  = origem

    while abs(angulo - destino) > passo:
        angulo += direcao * passo
        servo.angle = round(angulo, 1)
        time.sleep(delay)

    # Garante que chegamos exatamente no destino
    servo.angle = destino


# ---------------------------------------------------------------------------
# Varreduras
# ---------------------------------------------------------------------------
def varredura_horizontal(pan: Servo,
                         min_grau: float = 0.0,
                         max_grau: float = 180.0,
                         pontos: int = 7) -> None:
    """
    Varre o servo PAN de min_grau até max_grau passando por 'pontos'
    posições igualmente espaçadas, usando movimento suave entre cada uma.
    Retorna ao centro ao final.
    """
    print("\n── Varredura horizontal (PAN) ──")
    intervalo = (max_grau - min_grau) / (pontos - 1)
    posicoes  = [round(min_grau + i * intervalo, 1) for i in range(pontos)]

    for grau in posicoes:
        print(f"  PAN → {grau}°", end="", flush=True)
        mover_suave(pan, grau)
        print(f"  ✓")
        time.sleep(DELAY_DESTINO)

    print("  PAN → 90° (centro)", end="", flush=True)
    mover_suave(pan, 90.0)
    print("  ✓")


def varredura_vertical(tilt: Servo,
                       min_grau: float = 45.0,
                       max_grau: float = 135.0,
                       pontos: int = 5) -> None:
    """
    Varre o servo TILT entre min_grau e max_grau passando por 'pontos'
    posições igualmente espaçadas, usando movimento suave entre cada uma.
    Retorna ao centro ao final.
    """
    print("\n── Varredura vertical (TILT) ──")
    intervalo = (max_grau - min_grau) / (pontos - 1)
    posicoes  = [round(min_grau + i * intervalo, 1) for i in range(pontos)]

    for grau in posicoes:
        print(f"  TILT → {grau}°", end="", flush=True)
        mover_suave(tilt, grau)
        print("  ✓")
        time.sleep(DELAY_DESTINO)

    print("  TILT → 90° (centro)", end="", flush=True)
    mover_suave(tilt, 90.0)
    print("  ✓")


def posicao_inicial(pan: Servo, tilt: Servo) -> None:
    """Move ambos os servos para o centro de forma suave."""
    print("\n── Posição inicial (centro) ──")
    mover_suave(pan,  90.0)
    mover_suave(tilt, 90.0)
    time.sleep(0.3)
    print("  Servos centralizados ✓")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 50)
    print("  Rover – Controle de Câmera Pan/Tilt")
    print("  PCA9685 Plugin próprio (sem Adafruit)")
    print("=" * 50)
    print(f"\n  Passo:  {PASSO_GRAUS}° por iteração")
    print(f"  Delay:  {DELAY_PASSO * 1000:.0f} ms entre passos")
    vel = PASSO_GRAUS / DELAY_PASSO
    print(f"  Vel.:   ~{vel:.0f}°/s (movimento suave)\n")

    with PCAServos(address=0x40, bus=1, frequency=50) as pca:
        pan  = Servo(pca, channel=0, min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=1, min_pulse_us=600, max_pulse_us=2400)

        posicao_inicial(pan, tilt)

        print(f"\n  PAN  atual: {pan.angle}°")
        print(f"  TILT atual: {tilt.angle}°")

        varredura_horizontal(pan)
        time.sleep(0.5)

        varredura_vertical(tilt)
        time.sleep(0.5)

        # Aponta para posição específica de forma suave
        print("\n── Posição personalizada ──")
        print("  Movendo para PAN=45°  TILT=60°...")
        mover_suave(pan,  45.0)
        mover_suave(tilt, 60.0)
        print(f"  PAN={pan.angle}°  TILT={tilt.angle}°  ✓")
        time.sleep(1.0)

        posicao_inicial(pan, tilt)

    print("\nDemo finalizado. Servos desativados.")


if __name__ == "__main__":
    main()
