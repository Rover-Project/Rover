"""
control/keyboard_control.py
============================
Controle dos servos de câmera via teclado no terminal.

Mapeamento de teclas
---------------------
  ← / → (ou A / D)  : move o servo PAN  (horizontal) para esquerda/direita
  ↑ / ↓ (ou W / S)  : move o servo TILT (vertical)   para cima/baixo
  C                  : centraliza ambos os servos
  + / -              : aumenta ou diminui a velocidade de movimento
  Q ou ESC           : encerra o programa

Lógica de movimento suave (importante)
-----------------------------------------
Em vez de mover o servo imediatamente a cada tecla lida, este programa
separa "detectar tecla" de "mover o servo" em duas tarefas independentes:

  1) Uma thread fica só lendo o teclado e atualizando quais teclas estão
     PRESSIONADAS NESTE INSTANTE (um conjunto / set).
  2) O loop principal roda em um intervalo de tempo FIXO (ex.: a cada 20ms)
     e, a cada ciclo, aplica um pequeno incremento de ângulo para cada
     tecla que estiver no conjunto de "pressionadas".

Isso resolve dois problemas ao mesmo tempo:
  - Um toque rápido (tap) sempre produz pelo menos um pequeno movimento,
    porque o loop de movimento não depende de "quantos eventos de tecla"
    o sistema operacional gerou.
  - Segurar a tecla nunca acelera o servo de forma descontrolada, porque
    o incremento por ciclo é sempre o mesmo valor fixo, não importa quantos
    eventos de "tecla repetida" o terminal mande.

Execute na Raspberry Pi:
    pip install smbus2
    python control/keyboard_control.py
"""

import sys
import os
import tty
import termios
import threading
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pca9685 import PCAServos, Servo

logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Configuração dos servos
# ---------------------------------------------------------------------------
PAN_CHANNEL  = 0
TILT_CHANNEL = 1

PAN_MIN,  PAN_MAX  = 0.0, 180.0
TILT_MIN, TILT_MAX = 45.0, 135.0

# ---------------------------------------------------------------------------
# Configuração de velocidade — ajuste estes dois valores para
# tornar o movimento mais rápido ou mais lento.
# ---------------------------------------------------------------------------
TICK_INTERVAL   = 0.02   # segundos entre cada ciclo do loop de movimento (50 Hz)
DEGREES_PER_TICK = 0.6   # graus movidos por ciclo enquanto a tecla está pressionada
#   velocidade resultante = DEGREES_PER_TICK / TICK_INTERVAL  (graus por segundo)
#   valor atual: 0.6 / 0.02 = 30°/s — suave e previsível

SPEED_MIN = 0.2
SPEED_MAX = 3.0

# ---------------------------------------------------------------------------
# Estado compartilhado entre a thread de teclado e o loop de movimento
# ---------------------------------------------------------------------------
pressed_keys = set()        # teclas atualmente pressionadas
state_lock   = threading.Lock()
running      = True


# ---------------------------------------------------------------------------
# Thread de leitura de teclado
# ---------------------------------------------------------------------------
def keyboard_reader():
    """
    Lê o teclado continuamente em modo raw, com timeout curto.

    Como não há um evento nativo de "tecla solta" no terminal, usamos uma
    técnica de expiração: toda vez que uma tecla é lida, ela é marcada como
    pressionada com um timestamp. Se nenhuma leitura nova da mesma tecla
    chegar dentro de TIMEOUT_SOLTA segundos, o loop principal a considera
    solta automaticamente. Isso simula key-up/key-down de forma confiável
    mesmo em terminais que não enviam esses eventos.
    """
    global running

    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setraw(fd)

    try:
        while running:
            ch = sys.stdin.read(1)

            if ch == "\x1b":
                # Pode ser uma seta (ESC [ A/B/C/D) ou a tecla ESC isolada.
                # Usamos select com timeout curto para diferenciar.
                import select
                r, _, _ = select.select([sys.stdin], [], [], 0.01)
                if r:
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1) if ch2 == "[" else ""
                    key = ch + ch2 + ch3
                else:
                    key = "\x1b"   # ESC isolado → sair
            else:
                key = ch

            now = time.time()
            with state_lock:
                last_seen[key] = now

                if key in ("q", "Q", "\x1b"):
                    running = False
                elif key in ("c", "C"):
                    pending_actions.append("center")
                elif key == "+":
                    pending_actions.append("speed_up")
                elif key == "-":
                    pending_actions.append("speed_down")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# Timestamp da última vez que cada tecla de movimento foi lida
last_seen = {}
pending_actions = []   # ações de disparo único (centralizar, ajustar velocidade)

KEY_TIMEOUT = 0.15   # se não receber a tecla de novo em 150ms, considera solta

MOVE_KEYS = {
    "\x1b[D": "pan_neg",  "a": "pan_neg",  "A": "pan_neg",
    "\x1b[C": "pan_pos",  "d": "pan_pos",  "D": "pan_pos",
    "\x1b[A": "tilt_pos", "w": "tilt_pos", "W": "tilt_pos",
    "\x1b[B": "tilt_neg", "s": "tilt_neg", "S": "tilt_neg",
}


def active_directions() -> set:
    """Retorna o conjunto de direções atualmente 'pressionadas' (não expiradas)."""
    now = time.time()
    active = set()
    with state_lock:
        for key, direction in MOVE_KEYS.items():
            ts = last_seen.get(key)
            if ts is not None and (now - ts) <= KEY_TIMEOUT:
                active.add(direction)
    return active


# ---------------------------------------------------------------------------
# Interface de terminal
# ---------------------------------------------------------------------------
def print_header():
    print("\033[2J\033[H", end="")
    print("╔══════════════════════════════════════════╗")
    print("║     Rover — Controle de Câmera           ║")
    print("║     Plugin PCA9685 — Controle de Servos  ║")
    print("╠══════════════════════════════════════════╣")
    print("║  ←/A  →/D  : PAN  (horizontal)          ║")
    print("║  ↑/W  ↓/S  : TILT (vertical)            ║")
    print("║  C         : Centralizar                 ║")
    print("║  + / -     : Ajustar velocidade          ║")
    print("║  Q / ESC   : Sair                        ║")
    print("╚══════════════════════════════════════════╝")
    print()


def print_status(pan_angle: float, tilt_angle: float, speed_mult: float, last_action: str):
    bar_width = 30

    def bar(value, min_v, max_v):
        ratio = (value - min_v) / (max_v - min_v)
        filled = round(ratio * bar_width)
        return "█" * filled + "░" * (bar_width - filled)

    sys.stdout.write("\033[9;0H")
    print(f"  PAN  (horiz.): {pan_angle:6.1f}°  [{bar(pan_angle,  PAN_MIN,  PAN_MAX)}]")
    print(f"  TILT (vert.) : {tilt_angle:6.1f}°  [{bar(tilt_angle, TILT_MIN, TILT_MAX)}]")
    print(f"  Velocidade   : {speed_mult:.1f}x  (~{DEGREES_PER_TICK * speed_mult / TICK_INTERVAL:.0f}°/s)")
    print(f"  Última ação  : {last_action:<35}")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Loop principal de movimento — roda em intervalo fixo
# ---------------------------------------------------------------------------
def main():
    global running

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
    speed_mult = 1.0
    last_action = "Servos centralizados"

    print("  ✓ Conectado! Use as teclas descritas acima.\n\n\n\n\n")
    print_status(pan_angle, tilt_angle, speed_mult, last_action)

    reader_thread = threading.Thread(target=keyboard_reader, daemon=True)
    reader_thread.start()

    try:
        while running:
            cycle_start = time.time()

            # Processa ações de disparo único (centralizar, velocidade)
            with state_lock:
                actions = pending_actions[:]
                pending_actions.clear()

            for action in actions:
                if action == "center":
                    pan_angle, tilt_angle = 90.0, 90.0
                    pan.center()
                    tilt.center()
                    last_action = "Centralizado (90° / 90°)"
                elif action == "speed_up":
                    speed_mult = min(SPEED_MAX, speed_mult + 0.2)
                    last_action = f"Velocidade ↑ {speed_mult:.1f}x"
                elif action == "speed_down":
                    speed_mult = max(SPEED_MIN, speed_mult - 0.2)
                    last_action = f"Velocidade ↓ {speed_mult:.1f}x"

            # Aplica movimento contínuo baseado nas teclas atualmente pressionadas
            directions = active_directions()
            step = DEGREES_PER_TICK * speed_mult
            moved = False

            if "pan_neg" in directions:
                pan_angle = max(PAN_MIN, pan_angle - step)
                moved = True
            if "pan_pos" in directions:
                pan_angle = min(PAN_MAX, pan_angle + step)
                moved = True
            if "tilt_pos" in directions:
                tilt_angle = min(TILT_MAX, tilt_angle + step)
                moved = True
            if "tilt_neg" in directions:
                tilt_angle = max(TILT_MIN, tilt_angle - step)
                moved = True

            if moved:
                pan.angle  = pan_angle
                tilt.angle = tilt_angle
                last_action = f"PAN={pan_angle:.1f}°  TILT={tilt_angle:.1f}°"

            print_status(pan_angle, tilt_angle, speed_mult, last_action)

            # Dorme o tempo restante do ciclo, para manter o intervalo fixo
            elapsed = time.time() - cycle_start
            time.sleep(max(0.0, TICK_INTERVAL - elapsed))

    except KeyboardInterrupt:
        pass
    finally:
        running = False
        pan.center()
        tilt.center()
        pca.close()
        print("\n\n  ✓ Servos centralizados. Conexão encerrada.")


if __name__ == "__main__":
    main()
