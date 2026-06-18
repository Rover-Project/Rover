"""
tests/teste_manual_motor_style.py
====================================
Teste manual da interface forward/backward/stop/cleanup, simulando
exatamente o padrão de uso do script de integração com a câmera —
mas SEM precisar de hardware (PCA9685 físico) nem da câmera.

Use este script para verificar rapidamente, com os próprios olhos no
terminal, que a API se comporta como esperado antes de testar com
hardware real conectado.

Execução (do diretório raiz do projeto):
    python tests/teste_manual_motor_style.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

# Instala o mock do smbus2 ANTES de importar o pca9685,
# para não precisar do PCA9685 físico conectado.
from mock_smbus2 import install_mock
mock_bus = install_mock()

from pca9685 import PCAServos


def mostrar_estado(servos: PCAServos, canal: int, rotulo: str) -> None:
    on, off = servos.get_pwm(canal)
    duty_pct = off / 4096 * 100
    print(f"    {rotulo} (canal {canal}): ON={on:4d}  OFF={off:4d}  ({duty_pct:5.1f}% duty cycle)")


def main() -> None:
    print("=" * 60)
    print("  Teste manual — interface forward/backward/stop/cleanup")
    print("  (sem hardware — usando mock do barramento I2C)")
    print("=" * 60)

    FREQUENCY_SERVOS = 50
    SPEED = 50
    SERVO_V = 1
    SERVO_H = 0

    print("\n[1] Instanciando PCAServos(FREQUENCY_SERVOS)...")
    servos = PCAServos(FREQUENCY_SERVOS)
    print(f"    ✓ {servos}")

    print("\n[2] Testando forward() no servo vertical...")
    servos.forward(channels=(SERVO_V), speed=SPEED)
    mostrar_estado(servos, SERVO_V, "TILT")

    print("\n[3] Testando backward() no servo horizontal...")
    servos.backward(channels=(SERVO_H), speed=SPEED)
    mostrar_estado(servos, SERVO_H, "PAN ")

    print("\n[4] Testando stop() em ambos os canais...")
    servos.stop(channels=(SERVO_V, SERVO_H))
    mostrar_estado(servos, SERVO_V, "TILT")
    mostrar_estado(servos, SERVO_H, "PAN ")
    print("    (esperado: ambos devem voltar para ~307, o pulso neutro)")

    print("\n[5] Testando velocidade máxima forward()...")
    servos.forward(channels=SERVO_H, speed=100)
    mostrar_estado(servos, SERVO_H, "PAN ")

    print("\n[6] Testando velocidade máxima backward()...")
    servos.backward(channels=SERVO_H, speed=100)
    mostrar_estado(servos, SERVO_H, "PAN ")

    print("\n[7] Testando múltiplos canais simultâneos...")
    servos.forward(channels=(SERVO_V, SERVO_H), speed=75)
    mostrar_estado(servos, SERVO_V, "TILT")
    mostrar_estado(servos, SERVO_H, "PAN ")

    print("\n[8] Testando cleanup()...")
    servos.cleanup()
    print("    ✓ cleanup() executado sem erros")

    print("\n" + "=" * 60)
    print("  ✓ Todos os passos manuais executados com sucesso!")
    print("  Próximo passo: testar com hardware real na Raspberry Pi.")
    print("=" * 60)


if __name__ == "__main__":
    main()
