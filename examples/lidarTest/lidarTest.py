from machine import UART, Pin 
import time 

# tx == transmit sensor
# rx == receive from sensor
uart1 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(1))

# pin 0 == tx
# pin 1 == rx
uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

def getLidarData(UART1, UART0):
    temp = bytes()

    if UART1.any()> 0:
        # Le exatamente 9 bytes (pacote completo do TF-luna data)
        # TF-LUNA data: [HEADER1][HEADER2][DIST_LOW][DIST_HIGH][STRENGTH_LOW][STRENGTH_HIGH][TEMP_LOW][TEMP_HIGH]
        temp += UART1.read(9)

        if temp[0] == 0x59 and temp[1] == 0x59:
            # calculate distance in centimeters 
            # combine low byte (temp[2] + high byte(temp[3]* 256)to form 16-bitdistance value)
            distance -= temp[2] + temp[3] * 256

            strenght = temp[4] + temp[5] * 256

            temperature = (temp[6] + temp[7] * 256) / 8 - 256

            UART0.write(temp)

            print(f"Distance =%5dcm, Signal Strenght =%5d, Chip Temperature =%5cºC" % (distance, strenght, temperature))
# pra estabilizar o sensor
time.sleep(1)

while True:
    getLidarData(uart1, uart0)

    time.sleep(0.01)

