from gpiozero import Servo
from time import sleep

class servoMotor():
    def __init__(self):
        """
        Plugin para motores Servo, o qual possibilita sua configuração e controle
        """
        self.servo = None
        self.motor_type = "180"
        self.ritmo = 0.1
        self.move = False
        

    def start(self, pin:int, motor_type="180",ritmo = 0.1, initial_value=0, min_pulse_width=1/1000,
                 max_pulse_width=2/1000, frame_width=20/1000):
        """
        Inicia o motor. 
        Dica: Ajustar min_pulse e max_pulse resolve a maioria das trepidações.
        Args:
            pin: Pin (GPIO) no qual deseja se iniciar o Motor Servo 
            motor_type: String com o tipo do motor (Gira 180 ou 360 graus) 
            ritmo: Intervalo para acrescimo manual da posicao do Lidar
            initial_value: Define a posicao inicial do Motor ([-1, 1])
            min_pulse: Corresponde a posicao minima do Servo (padrao = 1ms)
            max_pulse: Corresponde a posicao maxima do Servo (padrao = 2ms)
            frame_width: Duracao de tempo entre cada pulso do Servo (padrao = 20ms)

            Dica: Em motores que giram em 360, nao se controla o angulo, mas sim
            a velocidade de giro. (Ou seja, 1 no value nao define 360 graus, mas girar em velocidade maxima
            para a direita)
        """
        try:
            # Atribuindo diretamente ao self.servo
            self.servo = Servo(
                pin, 
                initial_value=initial_value, 
                min_pulse_width=min_pulse_width, 
                max_pulse_width=max_pulse_width, 
                frame_width=frame_width
            )
            self.motor_type = motor_type
            self.ritmo = ritmo
            self.move = True
            print(f"Motor {motor_type} iniciado no GPIO {pin}")
        except Exception as e:
            print(f"Erro ao iniciar o servo: {e}")
            self.servo = None

    def set_min_position(self):
        """
        Ajusta o motor para a sua posicao minima (value = -1)
        """
        try:
            self.servo.min()
            sleep(0.5)
            print("Motor na posicao minima")
        except Exception as e:
            print(f"Error {e}")

    def set_mid_position(self):
        """
        Ajusta o motor para a seu ponto medio (value = 0)
        """
        try:
            self.servo.mid()
            sleep(0.5)
            print("Motor no ponto medio")
        except Exception as e:
            print(f"Error {e}")

    def set_max_position(self):
        """
        Ajusta o motor para a sua posicao maxima (value = 1)
        """
        try:
            self.servo.max()
            sleep(0.5)
            print("Motor na posicao maxima")
        except Exception as e:
            print(f"Error {e}")

    def set_value_position(self, value:float):
        """
        Passa um valor especifico para definir a posicao do Servo
        """
        self.move = True
        if value is None or not (-1 <= value <= 1):
                print("Passe um valor valido [-1, 1]")
                raise ValueError
        
        if self.servo.value is None:
            if self.move:
                self.servo.value = value # Reativa no valor desejado
            else:
                print("O modo de movimento nao esta ativado")
            
        else:
            self.servo.value = value
        
        sleep(0.5)

    def smooth_move(self, target_value: float, duration: float = 1.0):
        """
        Move o servo suavemente até a posição desejada.
        Args:
            target_value: Posição final [-1, 1].
            duration: Tempo total do movimento em segundos.
        """
        if not self.servo: return
        
        current_val = self.servo.value
        # Se não houver valor atual (servo recém ligado), assume o centro
        if current_val is None: current_val = 0 
        
        steps = 50  # Número de micro-passos
        step_delay = duration / steps
        delta = (target_value - current_val) / steps
        
        for _ in range(steps):
            current_val += delta
            self.servo.value = current_val
            sleep(step_delay)

    def set_interval_positions(self, values_list:list, smooth: bool = True):
        """
        Metodo aceita uma lista com valores de variacao para o servo motor
        Visando uma serie de testes pratica
        """
        if not values_list:
            print("Defina valores para movimentar o servo motor")
            raise ValueError

        for value in values_list:
            if value is None or not (-1 <= value <= 1):
                continue

            if smooth:
                self.smooth_move(value)
            else:
                self.set_value_position(value)
                sleep(0.5)

    def increase_value_position(self):
        """
        Modo interativo para ajuste fino e manual (self.ritmo = tamanho da variacao).
        """
        if not self.servo:
            print("Inicie o motor primeiro!")
            return
        
        print(f"Modo Manual Ativo (Ritmo: {self.ritmo})")
        while True:
            current_value = self.servo.value

            ch = str(input("Comand: [I] Aumentar, [D] Diminuir, [Q] Sair")).lower()

            if ch == "q":
                print("saindo do modo manual...")
                break

            if ch == "i":
                new_value = round(current_value + self.ritmo, 2)
                if new_value > 1:
                    print("Valor estorou o limite. Tente diminuir")
                else:
                    self.servo.value = new_value
            
            if ch == "d":
                new_value = round(current_value - self.ritmo, 2) # Pode ajudar com a tremedeira
                if new_value < -1:
                    print("Valor estourou o limite. Tente aumentar")
                    continue
                else:
                    self.servo.value = new_value

    def rotating_stop(self):
        """
        Atualiza o self.value do motor para None, o que faz que ele pare de tentar
        Girar, mas mantem a conexao ligada. (Para reativar, use self.set_value ou semelhante)
        """
        if self.servo:
            try:
                self.servo.detach() # Para de enviar pulsos
                self.move =False
                print("Movimentos do motor pausados")
            except Exception as e:
                print(f"Erro ao parar o motor: {e}")

    def stop(self):
        if self.servo:
            try:
                self.servo.detach()
                self.servo.close()  # Libera o pino GPIO
                self.servo = None
                print("Motor desligado e pinos liberados")
            except Exception as e:
                print(f"Erro ao parar o motor: {e}")
        