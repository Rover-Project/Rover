import ctypes
import time

# Carrega a biblioteca
lib = ctypes.CDLL("./libpin.so")

# Define os tipos das funções
lib.pin_create.argtypes = [ctypes.c_int, ctypes.c_int]
lib.pin_create.restype = ctypes.c_void_p

lib.pin_write.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.pin_read.argtypes = [ctypes.c_void_p]
lib.pin_read.restype = ctypes.c_int

lib.pin_destroy.argtypes = [ctypes.c_void_p]

# Constantes
OUTPUT = 1
INPUT = 0

# Cria pino (GPIO 15 = físico 10)
pin = lib.pin_create(15, OUTPUT)

try:
    for i in range(10):
        print("ON")
        lib.pin_write(pin, 1)
        time.sleep(1)

        print("OFF")
        lib.pin_write(pin, 0)
        time.sleep(1)

finally:
    print("Liberando pino")
    lib.pin_destroy(pin)
