import tkinter as tk
from tkinter import ttk
from motor import Motor

class AppControllerMotor:
    """
    Classe para criar e gerenciar a interface gráfica (Tkinter)
    e interagir com o objeto Motor.
    """
    def __init__(self, motor_controller: Motor):
        self.motor_controller = motor_controller
        self.root = tk.Tk()
        self.root.title("Controle do Rover")
        self.root.geometry("320x300")
        self.root.maxsize(320, 300)
        self.root.resizable(False, False)

        # Estado das direções para rastrear qual botão está pressionado
        self.direction_state = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
        }

        # Dicionário de métodos de movimento e seus loops agendados (para uso em `start/stop`)
        self.move_actions = {
            "forward": self.move_forward_loop,
            "backward": self.move_backward_loop,
            "left": self.move_left_loop,
            "right": self.move_right_loop,
        }
        
        self.setup_ui() # Setup para a interface
        self.update_speed_label() # Inicializa o label com o valor atual

    def setup_ui(self):
        """ Configura todos os componentes da interface Tkinter. """
        
        # Configura o grid da janela principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Frame central
        center_box = ttk.Frame(self.root, padding="10")
        center_box.grid(row=0, column=0, sticky="nsew") 

        # Configura as colunas do frame central
        for i in range(3):
            center_box.grid_columnconfigure(i, weight=1)

        # Título
        title_label = ttk.Label(center_box, text="Controle do Rover", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Label de Velocidade (Referência salva como atributo para atualização)
        self.speed_text = ttk.Label(center_box, text="", font=("Arial", 12))
        self.speed_text.grid(row=1, column=0, columnspan=3, pady=(0, 15))

        # Estilo para os botões de controle
        style = ttk.Style()
        style.configure('Control.TButton', font=('Arial', 12, 'bold'), padding=5)

        # Botões de movimento
        btn_up = ttk.Button(center_box, text="⬆️", style='Control.TButton')
        btn_up.grid(row=2, column=1, sticky="ew", padx=5, pady=5) 

        btn_left = ttk.Button(center_box, text="⬅️", style='Control.TButton')
        btn_left.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # Botões de velocidade
        btn_increase = ttk.Button(center_box, text="+ Velocidade", style='Control.TButton', command=self.increase_speed)
        btn_increase.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        btn_right = ttk.Button(center_box, text="➡️", style='Control.TButton')
        btn_right.grid(row=3, column=2, sticky="ew", padx=5, pady=5)

        btn_decrease = ttk.Button(center_box, text="- Velocidade", style='Control.TButton', command=self.decrease_speed)
        btn_decrease.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        btn_down = ttk.Button(center_box, text="⬇️", style='Control.TButton')
        btn_down.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Bind eventos
        btn_up.bind("<ButtonPress-1>", lambda e: self.start_movement("forward"))
        btn_up.bind("<ButtonRelease-1>", lambda e: self.stop_movement("forward"))
        btn_down.bind("<ButtonPress-1>", lambda e: self.start_movement("backward"))
        btn_down.bind("<ButtonRelease-1>", lambda e: self.stop_movement("backward"))
        btn_left.bind("<ButtonPress-1>", lambda e: self.start_movement("left"))
        btn_left.bind("<ButtonRelease-1>", lambda e: self.stop_movement("left"))
        btn_right.bind("<ButtonPress-1>", lambda e: self.start_movement("right"))
        btn_right.bind("<ButtonRelease-1>", lambda e: self.stop_movement("right"))

    def update_speed_label(self):
        """ Atualiza o texto do Label de velocidade. """
        self.speed_text.config(text=f"Velocidade: {self.motor_controller.speed:.1f}")

    def increase_speed(self):
        """ Aumenta a velocidade do motor e atualiza o label. """
        self.motor_controller.speed += 0.1
        self.update_speed_label()
        print(f"Velocidade atual: {self.motor_controller.speed:.1f}")

    def decrease_speed(self):
        """ Diminui a velocidade do motor e atualiza o label. """
        self.motor_controller.speed -= 0.1
        self.update_speed_label()
        print(f"Velocidade atual: {self.motor_controller.speed:.1f}")
    
    # Funções de loop para agendamento (chamadas recursivas via root.after)
    def move_forward_loop(self):
        if self.direction_state["forward"]:
            self.motor_controller.forward()
            print("Frente")
            self.root.after(100, self.move_forward_loop)
        else:
            self.motor_controller.stop()

    def move_backward_loop(self):
        if self.direction_state["backward"]:
            self.motor_controller.backward()
            print("Trás")
            self.root.after(100, self.move_backward_loop)
        else:
            self.motor_controller.stop()

    def move_left_loop(self):
        if self.direction_state["left"]:
            self.motor_controller.left()
            print("Esquerda")
            self.root.after(100, self.move_left_loop)
        else:
            self.motor_controller.stop()

    def move_right_loop(self):
        if self.direction_state["right"]:
            self.motor_controller.right()
            print("Direita")
            self.root.after(100, self.move_right_loop)
        else:
            self.motor_controller.stop()
            
    # --- Funções de Start/Stop genéricas ---
    def start_movement(self, direction):
        """ Inicia o loop de movimento para a direção especificada. """
        self.direction_state[direction] = True
        # Chama a função de loop correspondente para iniciar o movimento e o agendamento
        self.move_actions[direction]()

    def stop_movement(self, direction):
        """ Para o movimento para a direção especificada. """
        self.direction_state[direction] = False
        # A função de loop correspondente (ex: move_forward_loop) irá parar
        # o motor e não agendará a próxima chamada quando checar este estado.

    def run(self):
        """ Inicia o loop principal do Tkinter. """
        self.root.mainloop()