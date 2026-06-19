"""
examples/camera_pantilt.py
===========================
Controle de câmera Pan/Tilt travado estritamente para a faixa de 0 a 180 graus.
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
    sys.exit(1)

# Parâmetros de velocidade fluida
PASSO_GRAUS   = 2.0    
DELAY_PASSO   = 0.02   
DELAY_DESTINO = 0.5    

def mover_suave(servo: Servo, destino: float,
                passo: float = PASSO_GRAUS,
                delay: float = DELAY_PASSO) -> None:
    """
    Move o servo limitando rigorosamente o destino entre 0 e 180 graus.
    """
    # Trava de segurança via software para garantir que nenhuma entrada passe dos limites
    if destino < 0.0: destino = 0.0
    if destino > 180.0: destino = 180.0

    origem = servo.angle if (hasattr(servo, 'angle') and servo.angle is not None) else 90.0
    destino = float(destino)

    if abs(destino - origem) < 0.2:
        return

    direcao = 1.0 if destino > origem else -1.0
    angulo = origem

    while abs(angulo - destino) > passo:
        angulo += direcao * passo
        servo.angle = round(angulo, 1)
        time.sleep(delay)

    servo.angle = destino
    time.sleep(0.02)


def varredura_total(servo: Servo, nome_eixo: str) -> None:
    """
    Faz o servo percorrer a faixa completa de 0 a 180 graus,
    parando nos extremos e no centro.
    """
    print(f"\n── Varredura Total 180° ({nome_eixo}) ──")
    
    # 0° (Extremo inicial) -> 90° (Centro) -> 180° (Extremo final)
    posicoes = [0.0, 90.0, 180.0]

    for grau in posicoes:
        print(f"  {nome_eixo} → {grau}°", end="", flush=True)
        mover_suave(servo, grau)
        print("  ✓")
        time.sleep(DELAY_DESTINO)


def main() -> None:
    print("=" * 50)
    print("  Rover – Controle Pan/Tilt Limitado a 180°")
    print("=" * 50)

    with PCAServos(address=0x40, bus=1, frequency=50) as pca:
        pan  = Servo(pca, channel=0, min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=1, min_pulse_us=500, max_pulse_us=2500)

        # 1. Centraliza inicial
        print("\n── Centralizando em 90° ──")
        mover_suave(pan, 90.0)
        mover_suave(tilt, 90.0)
        time.sleep(0.5)

        # 2. Varreduras
        varredura_total(pan, "PAN")
        time.sleep(0.5)

        varredura_total(tilt, "TILT")
        time.sleep(0.5)

        # 3. Retorno ao Centro (CORREÇÃO AQUI)
        print("\n── Retornando ao Centro ──")
        mover_suave(pan, 90.0)
        mover_suave(tilt, 90.0)
        
        # ⚠️ ESPERA CRÍTICA: Dá tempo para o motor girar fisicamente até 90°
        # antes que o 'with' feche e desligue o PCA9685
        print("  Aguardando finalização do movimento físico...", end="", flush=True)
        time.sleep(1.5) 
        print(" ✓")

    print("\nTeste finalizado com sucesso.")

if __name__ == "__main__":
    main()
