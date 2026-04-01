from pin import Pin, PinMode

def main():
    pino = int(input("GPIO BCM [18]: ") or "18")
    modo = input("Modo (hw/sw) [hw]: ") or "hw"

    if modo == "hw":
        pin = Pin(pino, PinMode.PWM)
    else:
        pin = Pin(pino, PinMode.DIGITAL_OUT)

    print("Digite 'duty freq' (ex: 0.5 50) ou 'q' para sair.")

    try:
        while True:
            entrada = input("> ").strip()
            if entrada == "q":
                break
            partes = entrada.split()
            if len(partes) == 2:
                d, f = float(partes[0]), float(partes[1])
                pin.pwm(d, f)
                print(f"  duty={d:.3f}  freq={f} Hz  ativo={pin.active}")
            else:
                print("Formato: 0.075 50")
    finally:
        pin.release()
        print("Pino liberado.")

main()