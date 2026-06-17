"""
teste_conexao.py
==================
Teste de fumaça: verifica se a comunicação I2C com o PCA9685 está
funcionando, sem mover nenhum servo ainda.

Execute na Raspberry Pi com o PCA9685 conectado:
    python teste_conexao.py
"""

from pca9685 import PCAServos

print("Tentando conectar ao PCA9685 (endereço 0x40, bus 1)...")

try:
    pca = PCAServos(address=0x40, bus=1, frequency=50)
    print("✅ Conexão estabelecida com sucesso!")
    print(f"   {pca!r}")

    # Lê o estado atual de um canal (não move nada, só lê)
    on, off = pca.get_pwm(0)
    print(f"✅ Leitura do canal 0: ON={on} OFF={off}")

    pca.close()
    print("✅ Conexão encerrada corretamente.")
    print("\nTudo certo! Pode seguir para o teste de movimento do servo.")

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("   Solução: pip install smbus2")

except Exception as e:
    print(f"❌ Falha na comunicação I2C: {e}")
    print("   Verifique:")
    print("   - I2C habilitado (sudo raspi-config)")
    print("   - Fiação SDA/SCL correta")
    print("   - Endereço correto (rode: i2cdetect -y 1)")