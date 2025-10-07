from guizero import App, PushButton, Text, Box
from gpiozero import Robot
from ..constantes import LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2

# Criacao do motor, junto com a definicao dos pinos
motor = Robot(left=(LEFT_MOTOR_1, LEFT_MOTOR_2), right=(RIGHT_MOTOR_1, RIGHT_MOTOR_2))
motor_speed = 0.5

# Funcoes de controle
forward_pressed = backward_pressed = left_pressed = right_pressed = False

def move_forward_loop():
    """
        Move os dois motores para frente com a velocidade atual
    """  
    if forward_pressed:
        motor.forward(motor_speed) #type: ignore
        print("Frente")
        app.tk.after(100, move_forward_loop)
    else:
        motor.stop()

def move_backward_loop():
    """
        Move os dois motores para tras com a velocidade atual
    """
    if backward_pressed:
        motor.backward(speed=motor_speed) # type: ignore
        print("Trás")
        app.tk.after(100, move_backward_loop)
    else:
        motor.stop()

def move_left_loop():
    """
        Move apenas o motor esquerdo para frente com a velocidade atual
    """
    if left_pressed:
        motor.left(speed=motor_speed) # type: ignore
        print("Esquerda")
        app.tk.after(100, move_left_loop)
    else:
        motor.stop()

def move_right_loop():
    """
        Move apenas o motor direito para frente com a velocidade atual
    """ 
    if right_pressed:
        motor.right(speed=motor_speed) # type: ignore
        print("Direita")
        app.tk.after(100, move_right_loop)
    else:
        motor.stop()

def increase_speed():
    """
        Aumenta a velociade 10%, ate chegar ao maximo, 1.
    """
    global motor_speed
    
    if motor_speed + 0.1 > 1:
        motor_speed = 1

    elif motor_speed < 1.0:
        motor_speed += 0.1
        
    speed_text.value = f"Velocidade: {motor_speed:.1f}"
    print(f"Velocidade atual: {motor_speed:.1f}")

def decrease_speed():
    """
        Diminui a velocidade 10%, ate chegar ao minimo, 0.
    """
    global motor_speed

    if motor_speed - 0.1 < 0:
        motor_speed = 0
    
    elif motor_speed > 0:
        motor_speed -= 0.1
    speed_text.value = f"Velocidade: {motor_speed:.1f}"
    print(f"Velocidade atual: {motor_speed:.1f}")

# Start/Stop para cada direção
def start_forward():  global forward_pressed; forward_pressed=True; move_forward_loop()
def stop_forward():   global forward_pressed; forward_pressed=False
def start_backward(): global backward_pressed; backward_pressed=True; move_backward_loop()
def stop_backward():  global backward_pressed; backward_pressed=False
def start_left():     global left_pressed; left_pressed=True; move_left_loop()
def stop_left():      global left_pressed; left_pressed=False
def start_right():    global right_pressed; right_pressed=True; move_right_loop()
def stop_right():     global right_pressed; right_pressed=False

# Interface
app = App(title="Controle do Rover", layout="grid", height=500, width=400)
app.tk.maxsize(320,300)

# Box central que ocupa a janela inteira, agora com grid
center_box = Box(app, layout="grid", grid=[0,0], align="top", width="fill", height="fill")

# Título centralizado
Text(center_box, text="🎮 Controle do Rover", grid=[1,0])

# Velocidade centralizada
speed_text = Text(center_box, text=f"Velocidade: {motor_speed:.1f}", grid=[1,1])

# Botões movimento centralizados em cruz
btn_up = PushButton(center_box, text="⬆️", grid=[1,2], width=8, height=2)
btn_left = PushButton(center_box, text="⬅️", grid=[0,3], width=8, height=2)
btn_center = PushButton(center_box, text="⚙️ + Velocidade", grid=[1,3], width=12, height=1, command=increase_speed)
btn_decrease = PushButton(center_box, text="⚙️ - Velocidade", grid=[1,4], width=12, height=1, command=decrease_speed)
btn_right = PushButton(center_box, text="➡️", grid=[2,3], width=8, height=2)
btn_down = PushButton(center_box, text="⬇️", grid=[1,5], width=8, height=2)

# Bind eventos para responsividade
btn_up.tk.bind("<ButtonPress-1>", lambda event: start_forward())
btn_up.tk.bind("<ButtonRelease-1>", lambda event: stop_forward())
btn_down.tk.bind("<ButtonPress-1>", lambda event: start_backward())
btn_down.tk.bind("<ButtonRelease-1>", lambda event: stop_backward())
btn_left.tk.bind("<ButtonPress-1>", lambda event: start_left())
btn_left.tk.bind("<ButtonRelease-1>", lambda event: stop_left())
btn_right.tk.bind("<ButtonPress-1>", lambda event: start_right())
btn_right.tk.bind("<ButtonRelease-1>", lambda event: stop_right())

app.display()