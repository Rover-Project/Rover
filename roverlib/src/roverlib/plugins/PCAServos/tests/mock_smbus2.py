"""
tests/mock_smbus2.py
====================
Mock do smbus2 para testes unitários sem hardware físico.

Simula o comportamento do barramento I2C e dos registradores do PCA9685.
Registra todas as operações de leitura/escrita para inspeção nos testes.
"""

from collections import defaultdict
from unittest.mock import MagicMock
import sys


class MockSMBus:
    """
    Simulação do smbus2.SMBus para testes.

    Mantém um dicionário de registradores por endereço I2C e registra
    todas as chamadas de escrita/leitura.
    """

    def __init__(self, bus_number: int = 1):
        self.bus_number = bus_number
        # registradores[endereço][registrador] = valor
        self._registers: dict[int, dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.write_calls: list[tuple] = []   # (addr, reg, val)
        self.read_calls:  list[tuple] = []   # (addr, reg)

    def write_byte_data(self, address: int, register: int, value: int) -> None:
        self._registers[address][register] = value & 0xFF
        self.write_calls.append((address, register, value))

    def read_byte_data(self, address: int, register: int) -> int:
        self.read_calls.append((address, register))
        return self._registers[address][register]

    def close(self) -> None:
        pass

    def get_register(self, address: int, register: int) -> int:
        """Auxiliar de teste: lê registrador diretamente."""
        return self._registers[address][register]

    def set_register(self, address: int, register: int, value: int) -> None:
        """Auxiliar de teste: escreve registrador diretamente."""
        self._registers[address][register] = value & 0xFF


# ---------------------------------------------------------------------------
# Patch global: substitui smbus2 antes de importar o driver
# ---------------------------------------------------------------------------
def install_mock(mock_bus: MockSMBus | None = None) -> MockSMBus:
    """
    Instala o mock do smbus2 no sys.modules.

    Deve ser chamado ANTES de importar pca9685.

    Retorna
    -------
    MockSMBus
        A instância do mock que será usada pelo driver.
    """
    mock_module = MagicMock()
    bus = mock_bus or MockSMBus()
    mock_module.SMBus.return_value = bus
    sys.modules["smbus2"] = mock_module
    return bus
