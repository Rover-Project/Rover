"""
examples/camera_pantilt.py
===========================
Roteiro de teste em formato de Cruz (+) com SEGURANÇA MÁXIMA.
Movimentos lentos, controlados e travados rigorosamente entre 0° e 180°.
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

# ---------------------------------------------------------------------------
# Parâmetros de SEGURANÇA MÁXIMA (Movimento controlado, lento e visível)
# ---------------------------------------------------------------------------
PASSO_GRAUS   = 0.5    # Passo curtíssimo (meio grau por vez) para evitar trancos
DELAY_PASSO   = 0.05   # 50ms entre passos (~10° por segundo)
DELAY_DESTINO = 1.5    # Pausa longa nos extremos para estabilização mecânica

# ---------------------------------------------------------------------------
# Função de Movimentação Suave Blindada
# ---------------------------------------------------------------------------
def mover_suave(servo: Servo, destino: float,
                passo: float = PASSO_GRAUS,
                delay: float = DELAY_PASSO,
                origem_forcada: float = None) -> None:
    """
    Move o servo de forma incremental até o destino. 
    Usa 'origem_forcada' para garantir que o software nunca perca o sincronismo.
    """
    # Trava física via software: impede comandos fora de [0, 180]
    if destino < 0.0: destino = 0.0
    if destino > 180.0: destino = 180.0

    # Se passarmos a origem manualmente, usamos ela para evitar erros de leitura
    if origem_forcada is not None:
        origem = origem_forcada
    else:
        origem = servo.angle if (hasattr(servo, 'angle') and servo.angle is not None) else 90.0
    
    destino = float(destino)

    print(f"   [Calculando: {origem}° → {destino}°]", end="", flush=True)

    if abs(destino -伤rigem) < 0.2:
        print(" -> Já está no destino.")
        return

    direcao = 1.0 if destino > origem else -1.0
    angulo = origem

    # Loop forçado de passos lentos e graduais
    while abs(angulo - destino) > passo:
        angulo += direcao * passo
        servo.angle = round(angulo, 1)
        time.sleep(delay)

    # Garante a precisão exata no ponto final
    servo.angle = destino
    time.sleep(0.05)


# ---------------------------------------------------------------------------
# Execução Principal (Roteiro em Cruz Seguro)
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("  Rover – Teste Direcional em Cruz (Segurança Máxima)")
    print("=" * 60)
    print(f"  Configuração: {PASSO_GRAUS}° por passo a cada {DELAY_PASSO*1000:.0f}ms")
    print("  Velocidade Reduzida: ~10°/s (Prevenção de impactos mecânicos)\n")

    with PCAServos(address=0x40, bus=1, frequency=50) as pca:
        # Inicializa os servos calibrando a extensão total de pulso de 180°
        pan  = Servo(pca, channel=0, min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=1, min_pulse_us=500, max_pulse_us=2500)

        # -------------------------------------------------------------------
        # PASSO 1: Sincronização Inicial Elétrica (Home)
        # -------------------------------------------------------------------
        print("\n── [HOME] Forçando centralização mecânica em 90° ──")
        pan.angle = 90.0
        tilt.angle = 90.0
        print("  Aguardando alinhamento inicial dos motores...")
        time.sleep(2.5)  # Tempo estendido para garantir que saíram de qualquer posição antiga
        print("  Sincronizado! ✓")

        # -------------------------------------------------------------------
        # PASSO 2: Movimentação do Servo Horizontal (PAN)
        # -------------------------------------------------------------------
        print("\n── Iniciando Eixo Horizontal (PAN) ──")
        
        print("\n  PAN → 90° para a Direita (Ir para 180°)...", end="", flush=True)
        mover_suave(pan, destino=180.0, origem_forcada=90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  PAN → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(pan, destino=90.0, origem_forcada=180.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  PAN → 90° para a Esquerda (Ir para 0°)...", end="", flush=True)
        mover_suave(pan, destino=0.0, origem_forcada=90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  PAN → Voltar para o Meio (Ir para 90°)...", end="", flush=True)
        mover_suave(pan, destino=90.0, origem_forcada=0.0)
        print(" ✓")
        time.sleep(1.5)  # Pausa de transição entre os eixos

        # -------------------------------------------------------------------
        # PASSO 3: Movimentação do Servo Vertical (TILT)
        # -------------------------------------------------------------------
        print("\n── Iniciando Eixo Vertical (TILT) ──")

        print("\n  TILT → 90° para Baixo (Ir para 0°)...", end="", flush=True)
        mover_suave(tilt, destino=0.0, origem_forcada=90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  TILT → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(tilt, destino=90.0, origem_forcada=0.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  TILT → 90° para Cima (Ir para 180°)...", end="", flush=True)
        mover_suave(tilt, destino=180.0, origem_forcada=90.0)
        print(" ✓")
        time.sleep(DELAY_DESTINO)

        print("\n  TILT → Voltar para o Início (Ir para 90°)...", end="", flush=True)
        mover_suave(tilt, destino=90.0, origem_forcada=180.0)
        print(" ✓")

        # -------------------------------------------------------------------
        # PASSO 4: Encerramento com Trava de Tempo Física
        # -------------------------------------------------------------------
        print("\n── Finalizando Roteiro ──")
        print("  Segurando sinal ativo para conclusão dos movimentos...", end="", flush=True)
        time.sleep(2.0)  # Evita que o bloco 'with' corte a energia antes do tempo
        print(" ✓")

    print("\nSessão I2C finalizada. Ambos os servos parados e protegidos no centro (90°).")


if __name__ == "__main__":
    main()
