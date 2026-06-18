"""
examples/keyboard_control.py
============================
Controle dos servos de câmera via teclado no terminal.

Mapeamento de teclas
---------------------
  ← / → (ou A / D)  : move o servo PAN  (horizontal) para esquerda/direita
  ↑ / ↓ (ou W / S)  : move o servo TILT (vertical)   para cima/baixo
  C                  : centraliza ambos os servos
  + / -              : aumenta ou diminui o passo de movimento
  Q ou ESC           : encerra o programa

Execute na Raspberry Pi:
    pip install smbus2
    python control/keyboard_control.py
"""

import sys
import os
import tty
import termios
import logging

# Permite importar o pacote pca9685 da raiz do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pca9685 import PCAServos, Servo

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Configuração dos servos
# ---------------------------------------------------------------------------
PAN_CHANNEL  = 0   # Servo horizontal (esquerda/direita)
TILT_CHANNEL = 1   # Servo vertical   (cima/baixo)

PAN_MIN  = 0.0
PAN_MAX  = 180.0
TILT_MIN = 45.0    # Limita para não bater no mecanismo
TILT_MAX = 135.0

STEP_DEFAULT = 5.0  # graus por tecla pressionada
STEP_MIN     = 1.0
STEP_MAX     = 20.0

# ---------------------------------------------------------------------------
# Leitura de tecla sem pressionar Enter (modo raw)
# ---------------------------------------------------------------------------
def get_key() -> str:
    """Lê uma tecla pressionada sem precisar pressionar Enter."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Setas enviam sequências de escape: ESC [ A/B/C/D
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ---------------------------------------------------------------------------
# Interface de terminal
# ---------------------------------------------------------------------------
def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def print_header():
    print("\033[2J\033[H", end="")  # limpa o terminal
    print("╔══════════════════════════════════════════╗")
    print("║     Rover — Controle de Câmera           ║")
    print("║     Plugin PCA9685 — Controle de Servos  ║")
    print("╠══════════════════════════════════════════╣")
    print("║  ←/A  →/D  : PAN  (horizontal)          ║")
    print("║  ↑/W  ↓/S  : TILT (vertical)            ║")
    print("║  C         : Centralizar                 ║")
    print("║  + / -     : Ajustar passo               ║")
    print("║  Q / ESC   : Sair                        ║")
    print("╚══════════════════════════════════════════╝")
    print()

def print_status(pan_angle: float, tilt_angle: float, step: float, last_action: str):
    """Atualiza o status na tela sem limpar todo o terminal."""
    bar_width = 30

    def bar(value, min_v, max_v):
        ratio = (value - min_v) / (max_v - min_v)
        filled = round(ratio * bar_width)
        return "█" * filled + "░" * (bar_width - filled)

    sys.stdout.write("\033[9;0H")  # posiciona cursor na linha 9
    print(f"  PAN  (horiz.): {pan_angle:6.1f}°  [{bar(pan_angle,  PAN_MIN,  PAN_MAX)}]")
    print(f"  TILT (vert.) : {tilt_angle:6.1f}°  [{bar(tilt_angle, TILT_MIN, TILT_MAX)}]")
    print(f"  Passo atual  : {step:.1f}° por tecla")
    print(f"  Última ação  : {last_action:<35}")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------
def main():
    print_header()
    print("  Conectando ao PCA9685...")

    try:
        pca  = PCAServos(address=0x40, bus=1, frequency=50)
        pan  = Servo(pca, channel=PAN_CHANNEL,  min_pulse_us=500, max_pulse_us=2500)
        tilt = Servo(pca, channel=TILT_CHANNEL, min_pulse_us=600, max_pulse_us=2400)
    except Exception as e:
        print(f"\n  ✗ Falha ao conectar: {e}")
        print("    Verifique a fiação e se o I2C está habilitado (raspi-config).")
        sys.exit(1)

    pan.center()
    tilt.center()
    pan_angle  = 90.0
    tilt_angle = 90.0
    step       = STEP_DEFAULT
    last_action = "Servos centralizados"

    print("  ✓ Conectado! Use as teclas descritas acima.\n\n\n\n\n")
    print_status(pan_angle, tilt_angle, step, last_action)

    try:
        while True:
            key = get_key()

            prev_pan  = pan_angle
            prev_tilt = tilt_angle

            # ── PAN (horizontal) ──────────────────────────────────────────
            if key in ("\x1b[D", "a", "A"):   # ← ou A
                pan_angle = max(PAN_MIN, pan_angle - step)
                last_action = f"PAN ← {prev_pan:.1f}° → {pan_angle:.1f}°"
                pan.angle = pan_angle

            elif key in ("\x1b[C", "d", "D"): # → ou D
                pan_angle = min(PAN_MAX, pan_angle + step)
                last_action = f"PAN → {prev_pan:.1f}° → {pan_angle:.1f}°"
                pan.angle = pan_angle

            # ── TILT (vertical) ───────────────────────────────────────────
            elif key in ("\x1b[A", "w", "W"): # ↑ ou W
                tilt_angle = min(TILT_MAX, tilt_angle + step)
                last_action = f"TILT ↑ {prev_tilt:.1f}° → {tilt_angle:.1f}°"
                tilt.angle = tilt_angle

            elif key in ("\x1b[B", "s", "S"): # ↓ ou S
                tilt_angle = max(TILT_MIN, tilt_angle - step)
                last_action = f"TILT ↓ {prev_tilt:.1f}° → {tilt_angle:.1f}°"
                tilt.angle = tilt_angle

            # ── Centralizar ───────────────────────────────────────────────
            elif key in ("c", "C"):
                pan_angle  = 90.0
                tilt_angle = 90.0
                pan.center()
                tilt.center()
                last_action = "Centralizado (90° / 90°)"

            # ── Ajuste de passo ───────────────────────────────────────────
            elif key == "+":
                step = min(STEP_MAX, step + 1.0)
                last_action = f"Passo aumentado → {step:.0f}°"

            elif key == "-":
                step = max(STEP_MIN, step - 1.0)
                last_action = f"Passo diminuído → {step:.0f}°"

            # ── Sair ──────────────────────────────────────────────────────
            elif key in ("q", "Q", "\x1b"):
                last_action = "Encerrando..."
                print_status(pan_angle, tilt_angle, step, last_action)
                break

            print_status(pan_angle, tilt_angle, step, last_action)

    except KeyboardInterrupt:
        pass
    finally:
        pan.center()
        tilt.center()
        pca.close()
        print("\n\n  ✓ Servos centralizados. Conexão encerrada.")


if __name__ == "__main__":
    main()
