import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 1000  # e.g., LEDs at 1 kHz (servos would be 50)
# Each channel has a 16-bit duty_cycle: 0x0000..0xFFFF

ch = pca.channels[0]
for dc in (0x0000, 0x4000, 0x8000, 0xC000, 0xFFFF):
    ch.duty_cycle = dc
    time.sleep(0.5)

# For servos without ServoKit, set 50 Hz and compute pulse steps:
def set_servo_pulse_us(channel, pulse_us, freq=50):
    pca.frequency = freq
    period_us = 1_000_000 // freq       # 20,000 µs at 50 Hz
    step = int((pulse_us / period_us) * 0x10000)  # 16-bit duty steps
    pca.channels[channel].duty_cycle = max(0, min(0xFFFF, step))

# Example: ~1.0–2.0 ms servo range
set_servo_pulse_us(0, 1500)  # ~center