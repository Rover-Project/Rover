import time
import cv2
from .modules.movement import MovementModule
from .modules.camera import CameraModule
from .modules.vision import VisionModule

class Rover:
    
    # Classe principal da biblioteca Rover, responsável por inicializar e coordenar os módulos de Movimento, Câmera e Visão.
    
    def __init__(self, pwm_frequency=100):

        print("inicializando Rover...")
        self.movement = MovementModule(pwm_frequency=pwm_frequency)
        self.camera = CameraModule()
        self.vision = VisionModule(self.camera.get_preview_resolution())
        print("Rover inicializado com sucesso.")

    def follow_line(self, base_speed=30, kp=0.7, max_turn_speed=25, duration=None):
        
        # Algoritmo de Line Following usando a câmera.
        """
        Args:
            base_speed (int): Velocidade base para os motores (0-100).
            kp (float): Ganho Proporcional (Kp) para o controle PID simplificado.
            max_turn_speed (int): Velocidade máxima de correção de curva.
            duration (float, optional): Duração da execução em segundos. Se None, executa indefinidamente.
        """
        print(f"Iniciando modo Seguir Linha. Velocidade base: {base_speed}, Kp: {kp}")
        
        start_time = time.time()
        
        try:
            while True:
                if duration is not None and (time.time() - start_time) > duration:
                    print("Tempo de execução concluído.")
                    break

                frame = self.camera.capture_frame() # 1. Capturar o frame

                obstacle_detected, _ = self.vision.detect_obstacle(frame) # 2. Detecção de Obstáculos (Prioridade Máxima)
                
                if obstacle_detected:
                    print("Obstáculo detectado! Parando.")
                    self.movement.stop()
                    time.sleep(0.5) # pequena pausa para garantir a parada
                    
                    # possível lógica de desvio ou espera pode ser adicionada aqui
                    
                    continue # Volta ao início do loop para reavaliar

                
                desvio, processed_frame = self.vision.process_frame_for_line_following(frame) # 3. Processar o frame e obter o desvio da linha

                
                turn_speed = desvio * kp * base_speed # 4. Calcular a correção de velocidade (Controle Proporcional P)

                # 5. Aplicar a correção aos motores
                speed_left = base_speed - turn_speed
                speed_right = base_speed + turn_speed

                # Garantir que as velocidades estejam dentro dos limites (0-100)
                speed_left = max(0, min(100, speed_left))
                speed_right = max(0, min(100, speed_right))

                self.movement.move(speed_left, speed_right)
                
                # Opcional: Mostrar o frame processado (apenas para debug na RPi com display)
                # if processed_frame is not None:
                #     cv2.imshow("Processed Frame", processed_frame)
                #     if cv2.waitKey(1) & 0xFF == ord('q'):
                #         break
                
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("Interrupção pelo usuário.")
        finally:
            self.stop_and_cleanup()

    def stop_and_cleanup(self):
        """
        Para o Rover e limpa todos os recursos utilizados pelos módulos.
        """
        print("Parando e limpando recursos do Rover...")
        self.movement.stop()
        self.movement.cleanup()
        self.camera.cleanup()
        print("Limpeza concluída.")

# (teste)
if __name__ == "__main__":
    rover = None
    try:
        rover = Rover()
        
        print("Teste de seguir linha (simulado) por 5 segundos...")
        rover.follow_line(base_speed=30, duration=5)

    except Exception as e:
        print(f"Ocorreu um erro no teste principal: {e}")
    finally:
        
        if rover and 'stop_and_cleanup' in dir(rover):  # A limpeza já é chamada dentro de follow_line, mas garantimos aqui também
            pass
