"""
teste_conexao.py
==================
Teste de fumaça (smoke test): verifica se a comunicação I²C com o PCA9685
está funcionando, sem mover nenhum servo.

Ideal para rodar logo após a montagem eletrônica.

Execute na Raspberry Pi com o PCA9685 conectado:
  python teste_conexao.py
"""
from roverlib.plugins.PCAServos import PCAServos, HARDWARE_AVAILABLE

if not HARDWARE_AVAILABLE:
    print("❌ Bibliotecas da Adafruit/I²C indisponíveis.")
    print("   Rode na Raspberry Pi com: pip install adafruit-blinka adafruit-circuitpython-pca9685 adafruit-circuitpython-motor")
    raise SystemExit(1)

print("Tentando conectar ao PCA9685 (endereço 0x40, bus 1)...")

try:
    # Instancia o controlador (isso acorda o chip e configura a frequência)
    pca = PCAServos(address=0x40, frequency=50)
    print("✅ Conexão I²C estabelecida com sucesso!")
    print(f"   {pca!r}")

    # Lê o ciclo de trabalho atual do canal 0 (0 a 65535), sem alterá-lo
    duty = pca.pca.channels[0].duty_cycle
    print(f"✅ Leitura do canal 0: duty_cycle={duty}")
    print(f"✅ Frequência configurada: {pca.pca.frequency:.1f} Hz")

    pca.close()
    print("✅ Conexão encerrada corretamente.")
    print("\nTudo certo! Pode seguir para o teste de movimento (camera_pantilt.py).")

except Exception as e:
    print(f"❌ Falha na comunicação I²C: {e}")
    print("   Verifique:")
    print("   - Se o I²C está habilitado no sistema (sudo raspi-config)")
    print("   - A fiação SDA (dados) e SCL (clock)")
    print("   - O endereço hexadecimal (rode no terminal: i2cdetect -y 1)")
