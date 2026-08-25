"""
teste_conexao.py
==================
Teste de fumaça (Smoke Test): verifica se a comunicação I2C com o PCA9685 
está funcionando corretamente, sem mover nenhum servo.

Ideal para rodar logo após a montagem eletrônica para confirmar 
se os registradores estão respondendo.

Execute na Raspberry Pi com o PCA9685 conectado:
  python teste_conexao.py
"""

import sys
import os

# Permite rodar o script diretamente da pasta examples
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pca9685 import PCAServos

print("Tentando conectar ao PCA9685 (endereço 0x40, bus 1)...")

try:
    # Instancia o controlador (isso acorda o chip e configura o clock)
    pca = PCAServos(address=0x40, bus=1, frequency=50)
    print("✅ Conexão I2C estabelecida com sucesso!")
    print(f"   {pca!r}")

    # Lê o estado atual de um canal usando a leitura de 4 registradores
    on, off = pca.get_pwm(0)
    print(f"✅ Leitura do canal 0: ON={on} OFF={off}")

    # Encerra o barramento
    pca.close()
    print("✅ Conexão encerrada corretamente.")
    print("\nTudo certo! O hardware está respondendo de forma atômica.")
    print("Pode seguir para o teste de movimento (camera_pantilt.py).")

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("   Solução: pip install smbus2")

except Exception as e:
    print(f"❌ Falha na comunicação I2C: {e}")
    print("   Verifique:")
    print("   - Se o I2C está habilitado no sistema (sudo raspi-config)")
    print("   - A fiação SDA (Dados) e SCL (Clock)")
    print("   - O endereço hexadecimal (rode no terminal: i2cdetect -y 1)")
