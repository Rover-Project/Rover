"""
Exemplo de integração do MLObjectDetector com o sistema de movimento do Rover.
Este script demonstra como usar a detecção de ML com controle motor.
"""

import sys
import argparse
from pathlib import Path

try:
    from MLModelConfig import MLObjectDetector
except ImportError:
    print("[ERRO] MLModelConfig não encontrado no mesmo diretório")
    sys.exit(1)


class RoverMLVision:
    """
    Integra detecção de ML com movimento do Rover.
    
    Funcionalidade:
    - Detecta objetos usando ML
    - Calcula comandos de navegação
    - Controla movimento do rover
    """
    
    def __init__(
        self,
        model_path: str,
        camera_id: int = 0,
        confidence: float = 0.65,
        frame_width: int = 640,
        frame_height: int = 480,
        frame_skip: int = 2
    ):
        """
        Inicializa o Rover com visão ML.
        
        Args:
            model_path: Caminho do modelo ML
            camera_id: ID da câmera
            confidence: Limiar de confiança
            frame_width: Largura do frame
            frame_height: Altura do frame
            frame_skip: Skip de frames
        """
        print("[INFO] Inicializando Rover ML Vision")
        
        self.detector = MLObjectDetector(
            model_path=model_path,
            camera_id=camera_id,
            confidence=confidence,
            frame_width=frame_width,
            frame_height=frame_height,
            frame_skip=frame_skip
        )
        
        # Configuração de movimento
        self.motor_speed = 100  # 0-255
        self.turn_factor = 50   # Sensibilidade de rotação
        
        # Estado
        self.target_detected = False
        self.last_command = "IDLE"
        
        print("[OK] Rover ML Vision inicializado")

    def calculate_movement_command(self, detection: dict) -> dict:
        """
        Calcula comando de movimento baseado na detecção.
        
        Args:
            detection: Dicionário com informações de detecção
        
        Returns:
            dict com comando de movimento: {
                'left_motor': -255 a 255,
                'right_motor': -255 a 255,
                'status': string descrevendo ação
            }
        """
        center_x, center_y = detection['center']
        width = detection['width']
        height = detection['height']
        
        frame_center_x = self.detector.center_screen_x
        frame_center_y = self.detector.center_screen_y
        
        error_x = center_x - frame_center_x
        error_y = center_y - frame_center_y
        
        # Zonas de controle
        dead_zone_x = 30
        dead_zone_y = 40
        
        # Detecção de alvo alcançado
        if width > 150:
            return {
                'left_motor': 0,
                'right_motor': 0,
                'status': '🎯 ALVO ALCANCADO - PARAR'
            }
        
        # Movimento em Y (para frente/trás)
        if abs(error_y) > dead_zone_y:
            if error_y < 0:  # Objeto acima (longe)
                forward_speed = self.motor_speed
            else:  # Objeto abaixo (perto)
                forward_speed = -self.motor_speed
        else:
            forward_speed = 0
        
        # Movimento em X (esquerda/direita)
        if abs(error_x) > dead_zone_x:
            turn_amount = int((error_x / frame_center_x) * self.turn_factor)
            turn_speed = max(-self.motor_speed, min(self.turn_factor, turn_amount))
        else:
            turn_speed = 0
        
        # Calcular velocidade dos motores
        left_motor = forward_speed - turn_speed
        right_motor = forward_speed + turn_speed
        
        # Limitar range
        left_motor = max(-255, min(255, left_motor))
        right_motor = max(-255, min(255, right_motor))
        
        # Descrever ação
        if forward_speed > 0:
            status = f"⬆️ AVANCAR ({forward_speed})"
        elif forward_speed < 0:
            status = f"⬇️ RECUAR ({-forward_speed})"
        else:
            status = "➡️ ALINHANDO"
        
        if turn_speed < 0:
            status += f" VIRAR ESQUERDA"
        elif turn_speed > 0:
            status += f" VIRAR DIREITA"
        
        return {
            'left_motor': left_motor,
            'right_motor': right_motor,
            'status': status,
            'confidence': detection['confidence'],
            'class': detection['class_name']
        }

    def apply_motor_command(self, command: dict) -> None:
        """
        Aplica comando aos motores do rover.
        
        NOTA: Esta é uma versão simulada.
        Para hardware real, integre com:
        - rover_lib.modules.movement.control
        - GPIO/PWM do Raspberry Pi
        - Arduino/Motor drivers
        
        Args:
            command: Dicionário com velocidades dos motores
        """
        left_speed = command['left_motor']
        right_speed = command['right_motor']
        status = command['status']
        
        # Simulação de saída
        print(f"[MOTOR] L:{left_speed:4d} R:{right_speed:4d} | {status}")
        
        # TODO: Integrar com hardware real
        # from rover_lib.modules.movement import motor_controller
        # motor_controller.set_speed('left', left_speed)
        # motor_controller.set_speed('right', right_speed)

    def run(self, simulation_mode: bool = True) -> None:
        """
        Executa o loop de visão + movimento do rover.
        
        Args:
            simulation_mode: Se True, apenas simula (sem hardware real)
        """
        print("\n[INFO] Iniciando loop de movimento")
        print("[INFO] Pressione 'q' para sair\n")
        
        import cv2
        import time
        
        prev_time = time.time()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERRO] Falha ao capturar frame")
                break
            
            self.detector.frame_count += 1
            
            # Executar detecção
            if self.detector.frame_count % (self.detector.frame_skip + 1) == 0:
                try:
                    results = self.detector.model(
                        frame,
                        conf=self.detector.confidence,
                        verbose=False
                    )
                    result = results[0]
                    
                    self.detector.last_detections = []
                    
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        width = x2 - x1
                        height = y2 - y1
                        
                        if (width >= self.detector.MIN_WIDTH and
                            width <= self.detector.MAX_WIDTH and
                            height >= self.detector.MIN_HEIGHT and
                            height <= self.detector.MAX_HEIGHT):
                            
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            confidence = float(box.conf[0].cpu().numpy())
                            class_id = int(box.cls[0].cpu().numpy())
                            class_name = self.detector.model.names.get(class_id, "?")
                            
                            detection = {
                                'bbox': (x1, y1, x2, y2),
                                'center': (center_x, center_y),
                                'width': width,
                                'height': height,
                                'confidence': confidence,
                                'class_id': class_id,
                                'class_name': class_name
                            }
                            self.detector.last_detections.append(detection)
                
                except Exception as e:
                    print(f"[ERRO] Detecção falhou: {e}")
            
            # Calcular e aplicar movimento
            if self.detector.last_detections:
                # Usar maior detecção
                best_detection = max(
                    self.detector.last_detections,
                    key=lambda x: x['width'] * x['height']
                )
                
                command = self.calculate_movement_command(best_detection)
                self.apply_motor_command(command)
                self.target_detected = True
            else:
                # Sem detecção - parar
                self.apply_motor_command({
                    'left_motor': 0,
                    'right_motor': 0,
                    'status': '🔍 PROCURANDO...'
                })
                self.target_detected = False
            
            # Desenhar frame
            for detection in self.detector.last_detections:
                x1, y1, x2, y2 = detection['bbox']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                label = f"{detection['class_name']} {detection['confidence']:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Info
            fps = 1 / (time.time() - prev_time) if (time.time() - prev_time) > 0 else 0
            prev_time = time.time()
            
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Objetos: {len(self.detector.last_detections)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            status_icon = "🎯" if self.target_detected else "🔍"
            cv2.putText(frame, f"{status_icon} Mode: Movement", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow('Rover ML Vision - Movement Mode', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n[INFO] Encerrando...")
                break
        
        # Parar motores
        self.apply_motor_command({
            'left_motor': 0,
            'right_motor': 0,
            'status': '⏹️ PARADO'
        })
        
        self.detector.cap.release()
        cv2.destroyAllWindows()
        print("[OK] Finalizado")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Rover com Visão ML - Integração de Movimento'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='yolov8n.pt',
        help='Modelo ML a usar (padrão: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--camera', '-c',
        type=int,
        default=0,
        help='ID da câmera (padrão: 0)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.65,
        help='Limiar de confiança (padrão: 0.65)'
    )
    
    parser.add_argument(
        '--speed',
        type=int,
        default=100,
        help='Velocidade dos motores (0-255, padrão: 100)'
    )
    
    parser.add_argument(
        '--simulation',
        action='store_true',
        default=True,
        help='Modo simulação (sem hardware real)'
    )
    
    args = parser.parse_args()
    
    try:
        rover_vision = RoverMLVision(
            model_path=args.model,
            camera_id=args.camera,
            confidence=args.confidence
        )
        
        rover_vision.motor_speed = args.speed
        rover_vision.run(simulation_mode=args.simulation)
        
    except KeyboardInterrupt:
        print("\n[INFO] Interrupção do usuário")
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                 ROVER ML VISION - MOVEMENT MODE                ║
    ║                                                                ║
    ║  Integração de Detecção ML com Controle de Movimento do Rover ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    main()
