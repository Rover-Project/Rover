"""
examples/camera_pantilt.py
===========================
Roteiro de teste em formato de Cruz (+) avançando 90° para cada direção 
a partir do centro (90°), retornando sempre ao início.
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
DELAY_DESTINO = 0.8  # Pausa um pouco maior nos extremos para ficar claro o teste

# ---------------------------------------------------------------------------
# Função de Movimentação Suave com Trava de Segurança
# ---------------------------------------------------------------------------
def mover_suave(servo: Servo, destino: float,
                passo: float = PASSO_GRAUS,
                delay: float = DELAY_PASSO) -> None:
    """
    Move o servo de forma incremental até o destino. 
    Garante sincronia com a taxa de atualização do hardware (50Hz).
    """
    # Trava de segurança via software para garantir limites de 0 a 180
    if destino < 0.0: destino = 0.0
    if destino > 180.0: destino = 180.0

    origem = servo.angle if (hasattr(servo, 'angle') and servo.angle is not None) else 90.0
    destino = float(destino)

    if abs(destino - origem) < 0.2:
        return

    direcao = 1.0 if destino > origem else -1.0
    angulo = origin

    while abs(angulo - destino) > passo:
        angulo += direcao * passo
        servo.angle = round(angulo, 1)
        time.sleep(delay)

    # Garante a precisão final no destino exato
    servo.angle = destino
    time.sleep(0.02)


# ---------------------------------------------------------------------------
# Execução Principal (Roteiro em Cruz)
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 50)
    print("  Rover – Teste Direcional em Cruz (90° Extremos)")
    print("=" * 50)

    with PCAServos(address=0x40, bus=1, frequency=50) as pca:
        # Inicializa os servos utilizando toda a extensão de pulso de 180°
        pan  = Servo(pca, channel=0, min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=1, min_pulse_us=500, max_pulse_us=2500)

        # -------------------------------------------------------------------
        # PASSO 1: Sincronização e Posição Inicial (Centro)
        # -------------------------------------------------------------------
        print("\n── [HOME] Centralizando ambos os servos em 90° ──")
        mover_suave(pan, 90.0)
        mover_suave(tilt, 90.0)
        time.sleep(1.0)

        # -------------------------------------------------------------------
        # PASSO 2: Movimentação do Servo Horizontal (PAN)
        # -------------------------------------------------------------------
        print("\n── Iniciando Eixo Horizontal (PAN) ──")
        
        print("  PAN → 90° para a Direita (Ir para 180°)...", end="", flush=True)
        mover_suave(pan, 180.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("  PAN → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(pan, 90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("  PAN → 90° para a Esquerda (Ir para 0°)...", end="", flush=True)
        mover_suave(pan, 0.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("  PAN → Voltar para o Meio (Ir para 90°)...", end="", flush=True)
        mover_suave(pan, 90.0)
        print(" ✓")
        time.sleep(1.0)  # Pausa antes de trocar de eixo

        # -------------------------------------------------------------------
        # PASSO 3: Movimentação do Servo Vertical (TILT)
        # -------------------------------------------------------------------
        print("\n── Iniciando Eixo Vertical (TILT) ──")

        print("  TILT → 90° para Baixo (Ir para 0°)...", end="", flush=True)
        mover_suave(tilt, 0.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("  TILT → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(tilt, 90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("  TILT → 90° para Cima (Ir para 180°)...", end="", flush=True)
        mover_suave(tilt, 180.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        # -------------------------------------------------------------------
        # PASSO 4: Encerramento Seguro (Volta ao início e espera o motor chegar)
        # -------------------------------------------------------------------
        print("\n── Finalizando Roteiro ──")
        print("  TILT → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(tilt, 90.0)
        print(" ✓")
        
        # ⚠️ Aguarda o tempo do movimento físico acabar antes de fechar o barramento I2C
        print("  Aguardando finalização mecânica...", end="", flush=True)
        time.sleep(1.5)
        print(" ✓")

    print("\nSessão I2C fechada. Ambos os servos parados no centro (90°).")


if __name__ == "__main__":
    main()
