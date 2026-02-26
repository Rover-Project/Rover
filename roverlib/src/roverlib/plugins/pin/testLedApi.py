from pin import Pin, PinMode
import threading
import time
import sys

running = True

# Thread para capturar teclado
def keyboard_listener():
    global running
    while True:
        c = sys.stdin.read(1)
        if c.lower() == 'q':
            running = False
            break

def main():
    global running

    led = Pin(15, PinMode.OUTPUT)

    print("Pressione 'q' para parar...\n")

    # inicia thread do teclado
    t = threading.Thread(target=keyboard_listener, daemon=True)
    t.start()

    try:
        while running:
            print("LED ON")
            led.write(1)
            time.sleep(1)

            print("LED OFF")
            led.write(0)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrompido com CTRL+C")

    finally:
        print("Desligando LED e liberando GPIO...")

        # garante que o pino fica em LOW antes de sair
        try:
            led.write(0)
        except:
            pass

        # força destruição do objeto (chama destructor C++)
        del led

        print("Encerrado com sucesso ✔")

if __name__ == "__main__":
    main()
