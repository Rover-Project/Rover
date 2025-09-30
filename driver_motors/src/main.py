from gpiozero import Robot
import keyboard
import time

# Definir os pinos conforme os circuito
l1 = 11
l2 = 12
r1 = 15
r2 = 16

# Definição dos pinos da ponte H 
motor = Robot(left=(l1, l2), right=(r1, r2))

velocidade = 0.6  # velocidade 

print("Controle dos motores via teclado:")
print("Seta ↑ = Frente | Seta ↓ = Ré | Seta ← = Esquerda | Seta → = Direita | ESPAÇO = Parar | Q = Sair")

try:
    while True:
        if keyboard.is_pressed("up"):  # seta para cima
            motor.forward(velocidade)
            print("Frente")
        elif keyboard.is_pressed("down"):  # seta para baixo
            motor.backward(velocidade)
            print("Ré")
        elif keyboard.is_pressed("left"):  # seta para esquerda
            motor.left(velocidade)
            print("Esquerda")
        elif keyboard.is_pressed("right"):  # seta para direita
            motor.right(velocidade)
            print("Direita")
        elif keyboard.is_pressed("space"):  # barra de espaço
            motor.stop()
            print("Parado")
        elif keyboard.is_pressed("q"):  # tecla q para sair
            print("Saindo...")
            motor.stop()
            break
        
        time.sleep(0.1)  # evita loop muito rápido

except KeyboardInterrupt:
    motor.stop()
    print("\nPrograma encerrado.")
