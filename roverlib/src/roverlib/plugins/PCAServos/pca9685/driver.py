"""
pca9685/driver.py
=================
Driver de baixo nível para o PCA9685.

Comunicação I2C direta via smbus2 (sem dependência da Adafruit).

Referências do Datasheet NXP PCA9685
--------------------------------------
  • Endereço I2C padrão     : 0x40  (bits A5-A0 = 000000)
  • Clock interno            : ~25 MHz
  • Resolução PWM            : 12 bits (valores 0–4095)
  • Canais PWM               : 16 canais independentes
  • Frequência PWM configurável: 24 Hz a 1526 Hz

Mapa de Registradores (resumo)
--------------------------------
  0x00  MODE1       – configuração principal (sleep, restart, autoincrement…)
  0x01  MODE2       – saídas (OUTDRV, INVRT, OCH)
  0x06  LED0_ON_L   – canal 0 ON  byte baixo
  0x07  LED0_ON_H   – canal 0 ON  byte alto
  0x08  LED0_OFF_L  – canal 0 OFF byte baixo
  0x09  LED0_OFF_H  – canal 0 OFF byte alto
  … (cada canal ocupa 4 bytes; offset = canal × 4 + 0x06)
  0xFA  ALL_LED_ON_L  – seta todos os canais ON  (byte baixo)
  0xFB  ALL_LED_ON_H  – seta todos os canais ON  (byte alto)
  0xFC  ALL_LED_OFF_L – seta todos os canais OFF (byte baixo)
  0xFD  ALL_LED_OFF_H – seta todos os canais OFF (byte alto)
  0xFE  PRE_SCALE   – divisor de clock para frequência PWM

Cálculo da frequência (Datasheet §7.3.5)
------------------------------------------
  prescale = round(osc_clock / (4096 × freq)) − 1
  onde osc_clock = 25_000_000 Hz (clock interno padrão)

Comunicação I2C
-----------------
  write_byte_data(addr, register, value)  → escreve 1 byte em 1 registrador
  read_byte_data(addr, register)          → lê 1 byte de 1 registrador
"""

import time
import logging
from typing import Optional

try:
    import smbus2
except ImportError:
    smbus2 = None  # permite importar o módulo fora da Pi (testes/mock)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes – Registradores PCA9685 (Datasheet Tabela 4)
# ---------------------------------------------------------------------------
_REG_MODE1        = 0x00
_REG_MODE2        = 0x01
_REG_SUBADR1      = 0x02
_REG_SUBADR2      = 0x03
_REG_SUBADR3      = 0x04
_REG_ALLCALLADR   = 0x05
_REG_LED0_ON_L    = 0x06   # base; cada canal = base + canal*4
_REG_ALL_LED_ON_L = 0xFA
_REG_ALL_LED_ON_H = 0xFB
_REG_ALL_LED_OFF_L= 0xFC
_REG_ALL_LED_OFF_H= 0xFD
_REG_PRE_SCALE    = 0xFE
_REG_TESTMODE     = 0xFF

# Bits do registrador MODE1
_BIT_RESTART = 0x80   # 1 = reinicia todos os PWMs
_BIT_EXTCLK  = 0x40   # 1 = usa clock externo
_BIT_AI      = 0x20   # 1 = auto-increment de registrador
_BIT_SLEEP   = 0x10   # 1 = modo sleep (oscilador desligado)
_BIT_SUB1    = 0x08
_BIT_SUB2    = 0x04
_BIT_SUB3    = 0x02
_BIT_ALLCALL = 0x01

# Bits do registrador MODE2
_BIT_INVRT   = 0x10   # 1 = saída invertida
_BIT_OCH     = 0x08   # 0 = muda na borda STOP; 1 = muda na borda ACK
_BIT_OUTDRV  = 0x04   # 1 = totem-pole; 0 = open-drain

_OSC_CLOCK   = 25_000_000   # 25 MHz – oscilador interno padrão
_PWM_RESOLUTION = 4096      # 12 bits

_DEFAULT_ADDRESS = 0x40
_DEFAULT_I2C_BUS = 1        # /dev/i2c-1 na Raspberry Pi 5


# ---------------------------------------------------------------------------
# Exceções personalizadas
# ---------------------------------------------------------------------------
class PCA9685Error(Exception):
    """Erro base do driver PCA9685."""


class I2CError(PCA9685Error):
    """Falha de comunicação I2C."""


class InvalidChannelError(PCA9685Error):
    """Canal inválido (fora de 0–15)."""


class InvalidFrequencyError(PCA9685Error):
    """Frequência fora do range suportado (24–1526 Hz)."""


# ---------------------------------------------------------------------------
# Driver principal
# ---------------------------------------------------------------------------
class PCA9685Driver:
    """
    Driver de baixo nível para o PCA9685.

    Realiza toda comunicação via I2C sem dependência de bibliotecas externas
    além de smbus2.

    Parâmetros
    ----------
    address : int
        Endereço I2C do PCA9685. Padrão: 0x40.
    bus : int
        Número do barramento I2C da Raspberry Pi. Padrão: 1 (/dev/i2c-1).
    osc_clock : int
        Frequência do oscilador em Hz. Padrão: 25_000_000 (interno).

    Exemplo
    -------
    >>> driver = PCA9685Driver()
    >>> driver.set_frequency(50)          # 50 Hz para servos
    >>> driver.set_pwm(channel=0, on=0, off=307)  # ~7.5% duty cycle
    >>> driver.close()
    """

    def __init__(
        self,
        address: int = _DEFAULT_ADDRESS,
        bus: int = _DEFAULT_I2C_BUS,
        osc_clock: int = _OSC_CLOCK,
    ) -> None:
        self.address   = address
        self.osc_clock = osc_clock
        self._bus_num  = bus
        self._bus: Optional[smbus2.SMBus] = None
        self._frequency: Optional[float] = None

        self._open_bus()
        self._reset()
        logger.info(
            "PCA9685Driver inicializado | endereço=0x%02X bus=%d", address, bus
        )

    # ------------------------------------------------------------------
    # Interface pública – inicialização
    # ------------------------------------------------------------------

    def _open_bus(self) -> None:
        """Abre o barramento I2C."""
        if smbus2 is None:
            raise ImportError(
                "smbus2 não encontrado. Instale com: pip install smbus2"
            )
        try:
            self._bus = smbus2.SMBus(self._bus_num)
        except Exception as exc:
            raise I2CError(
                f"Não foi possível abrir o barramento I2C-{self._bus_num}: {exc}"
            ) from exc

    def _reset(self) -> None:
        """
        Inicializa o PCA9685 ao estado padrão.

        Sequência (Datasheet §7.3.1):
          1. Coloca em SLEEP para configurar PRE_SCALE
          2. Habilita auto-increment (AI) para escrita sequencial
          3. Sai do SLEEP com RESTART
        """
        # Passo 1: entra em sleep
        self._write_register(_REG_MODE1, _BIT_SLEEP | _BIT_AI)
        time.sleep(0.005)

        # Passo 2: sai do sleep e habilita RESTART + ALLCALL
        self._write_register(_REG_MODE1, _BIT_AI | _BIT_ALLCALL)
        time.sleep(0.005)

        # Passo 3: configura saídas em totem-pole (OUTDRV=1)
        self._write_register(_REG_MODE2, _BIT_OUTDRV)

        logger.debug("PCA9685 resetado e inicializado.")

    # ------------------------------------------------------------------
    # Frequência PWM
    # ------------------------------------------------------------------

    def set_frequency(self, frequency: float) -> None:
        """
        Configura a frequência PWM para todos os canais.

        Cálculo do PRE_SCALE (Datasheet §7.3.5):
            prescale = round(osc_clock / (4096 × freq)) − 1

        Faixa válida: 24 Hz – 1526 Hz

        Parâmetros
        ----------
        frequency : float
            Frequência desejada em Hz (50 Hz é o padrão para servos RC).

        Levanta
        -------
        InvalidFrequencyError
            Se a frequência estiver fora do range suportado.
        """
        if not (24 <= frequency <= 1526):
            raise InvalidFrequencyError(
                f"Frequência {frequency} Hz inválida. Range suportado: 24–1526 Hz."
            )

        prescale = round(self.osc_clock / (_PWM_RESOLUTION * frequency)) - 1
        prescale = max(3, min(255, prescale))   # clamp conforme datasheet

        logger.debug(
            "Configurando frequência: %.1f Hz → PRE_SCALE=0x%02X", frequency, prescale
        )

        # PRE_SCALE só pode ser alterado em modo SLEEP (Datasheet §7.3.5)
        old_mode = self._read_register(_REG_MODE1)
        sleep_mode = (old_mode & ~_BIT_RESTART) | _BIT_SLEEP
        self._write_register(_REG_MODE1, sleep_mode)
        self._write_register(_REG_PRE_SCALE, prescale)

        # Restaura o modo anterior e aguarda o oscilador estabilizar
        self._write_register(_REG_MODE1, old_mode)
        time.sleep(0.005)

        # Dispara RESTART para sincronizar todos os canais
        self._write_register(_REG_MODE1, old_mode | _BIT_RESTART)

        self._frequency = frequency
        logger.info("Frequência PWM configurada: %.1f Hz (PRE_SCALE=%d)", frequency, prescale)

    def get_frequency(self) -> Optional[float]:
        """Retorna a última frequência configurada (Hz), ou None se não configurada."""
        return self._frequency

    # ------------------------------------------------------------------
    # Controle de canais
    # ------------------------------------------------------------------

    def set_pwm(self, channel: int, on: int, off: int) -> None:
        """
        Configura os registradores ON e OFF de um canal específico.

        O PCA9685 controla cada canal com dois valores de 12 bits:
          • ON  : tick em que a saída vai para HIGH (0–4095)
          • OFF : tick em que a saída vai para LOW  (0–4095)

        O duty cycle efetivo = (off − on) / 4096

        Para servos, normalmente on=0 e off varia conforme o ângulo desejado.

        Registradores escritos (4 bytes por canal):
            base = 0x06 + canal * 4
            base+0 → ON_L  (byte baixo de ON)
            base+1 → ON_H  (byte alto  de ON)
            base+2 → OFF_L (byte baixo de OFF)
            base+3 → OFF_H (byte alto  de OFF)

        Parâmetros
        ----------
        channel : int
            Canal PWM (0–15).
        on : int
            Valor do tick de início HIGH (0–4095).
        off : int
            Valor do tick de início LOW  (0–4095).

        Levanta
        -------
        InvalidChannelError
            Se o canal estiver fora do range 0–15.
        """
        self._validate_channel(channel)
        on  = max(0, min(4095, int(on)))
        off = max(0, min(4095, int(off)))

        base = _REG_LED0_ON_L + channel * 4
        
        # Empacota os 4 bytes na ordem exata dos registradores
        data_block = [
            on & 0xFF,          # base+0: ON_L
            (on >> 8) & 0x0F,   # base+1: ON_H
            off & 0xFF,         # base+2: OFF_L
            (off >> 8) & 0x0F   # base+3: OFF_H
        ]
        
        try:
            # Envia o bloco inteiro em uma única transação I2C
            self._bus.write_i2c_block_data(self.address, base, data_block)
        except Exception as exc:
            raise I2CError(f"Falha ao escrever bloco PWM no canal {channel}: {exc}") from exc

        logger.debug("Canal %d atualizado atomicamente: ON=%d OFF=%d", channel, on, off)

    def set_duty_cycle(self, channel: int, value: int) -> None:
        """
        Define o duty cycle de um canal por valor absoluto (0–4095).

        Atalho para set_pwm(channel, on=0, off=value).

        Parâmetros
        ----------
        channel : int
            Canal PWM (0–15).
        value : int
            Valor de duty cycle de 0 (0%) a 4095 (100%).
        """
        self.set_pwm(channel, 0, value)

    def set_duty_cycle_percent(self, channel: int, percent: float) -> None:
        """
        Define o duty cycle de um canal em percentual (0.0–100.0).

        Parâmetros
        ----------
        channel : int
            Canal PWM (0–15).
        percent : float
            Percentual do duty cycle (ex.: 7.5 para posição neutra de servo).
        """
        percent = max(0.0, min(100.0, percent))
        value = round(percent / 100.0 * (_PWM_RESOLUTION - 1))
        self.set_pwm(channel, 0, value)

    def set_all_pwm(self, on: int, off: int) -> None:
        """
        Configura ON e OFF para TODOS os 16 canais simultaneamente.

        Utiliza os registradores especiais ALL_LED (0xFA–0xFD).

        Parâmetros
        ----------
        on : int
            Tick de início HIGH (0–4095).
        off : int
            Tick de início LOW  (0–4095).
        """
        on  = max(0, min(4095, int(on)))
        off = max(0, min(4095, int(off)))
        
        # Empacota os 4 bytes para os registradores ALL_LED
        data_block = [
            on & 0xFF,
            (on >> 8) & 0x0F,
            off & 0xFF,
            (off >> 8) & 0x0F
        ]
        
        try:
            # Envia para o endereço base _REG_ALL_LED_ON_L (0xFA)
            self._bus.write_i2c_block_data(self.address, _REG_ALL_LED_ON_L, data_block)
        except Exception as exc:
            raise I2CError(f"Falha ao escrever bloco ALL_LED: {exc}") from exc
            
        logger.debug("Todos os canais atualizados atomicamente: ON=%d OFF=%d", on, off)

    def get_pwm(self, channel: int) -> tuple[int, int]:
        """
        Lê os valores ON e OFF atuais de um canal.

        Retorna
        -------
        tuple[int, int]
            (on, off) — valores de 12 bits.
        """
        self._validate_channel(channel)
        base = _REG_LED0_ON_L + channel * 4
        try:
            on_l  = self._read_register(base + 0)
            on_h  = self._read_register(base + 1)
            off_l = self._read_register(base + 2)
            off_h = self._read_register(base + 3)
        except Exception as exc:
            raise I2CError(f"Falha ao ler canal {channel}: {exc}") from exc

        on  = on_l  | ((on_h  & 0x0F) << 8)
        off = off_l | ((off_h & 0x0F) << 8)
        return on, off

    def reset_channel(self, channel: int) -> None:
        """Define ON=0 e OFF=0 em um canal (saída inativa)."""
        self.set_pwm(channel, 0, 0)

    def reset_all_channels(self) -> None:
        """Desativa todos os 16 canais (ON=0, OFF=0)."""
        self.set_all_pwm(0, 0)

    # ------------------------------------------------------------------
    # I2C de baixo nível
    # ------------------------------------------------------------------

    def _write_register(self, register: int, value: int) -> None:
        """Escreve 1 byte em um registrador via I2C."""
        try:
            self._bus.write_byte_data(self.address, register, value)
        except Exception as exc:
            raise I2CError(
                f"Erro I2C write | addr=0x{self.address:02X} "
                f"reg=0x{register:02X} val=0x{value:02X}: {exc}"
            ) from exc

    def _read_register(self, register: int) -> int:
        """Lê 1 byte de um registrador via I2C."""
        try:
            return self._bus.read_byte_data(self.address, register)
        except Exception as exc:
            raise I2CError(
                f"Erro I2C read | addr=0x{self.address:02X} "
                f"reg=0x{register:02X}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_channel(channel: int) -> None:
        if not (0 <= channel <= 15):
            raise InvalidChannelError(
                f"Canal {channel} inválido. Use valores de 0 a 15."
            )

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Fecha o barramento I2C e libera recursos."""
        if self._bus:
            try:
                self.reset_all_channels()
                self._bus.close()
                logger.info("Barramento I2C fechado.")
            except Exception as exc:
                logger.warning("Erro ao fechar barramento I2C: %s", exc)
            finally:
                self._bus = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return (
            f"PCA9685Driver(address=0x{self.address:02X}, "
            f"bus={self._bus_num}, freq={self._frequency} Hz)"
        )
