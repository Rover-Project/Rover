"""
    python MLModelConfig.py --model path/to/model.pt --camera 0 --confidence 0.65
    python MLModelConfig.py --model best_int8.tflite --camera 0
    python MLModelConfig.py --model yolov8n.pt (baixa automático)
"""

import cv2
import argparse
import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple, List

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Aviso: ultralytics não instalado. Instale com: pip install ultralytics")


class MLObjectDetector:
    """
    Detector de objetos usando modelos de Machine Learning.
    
    Suporta:
    - YOLOv8 (diferentes tamanhos: nano, small, medium, large, xlarge)
    - Modelos customizados treinados com YOLO
    - Modelos em formato .pt, .onnx, .tflite
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
        Inicializa o detector de objetos.
        
        Args:
            model_path: Caminho para o modelo (.pt, .onnx, .tflite) ou nome do modelo YOLO
            camera_id: ID da câmera a usar (padrão: 0)
            confidence: Limiar de confiança para detecções (0.0-1.0)
            frame_width: Largura do frame capturado
            frame_height: Altura do frame capturado
            frame_skip: Número de frames a pular entre detecções (1 a cada N+1 frames)
        """
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("ultralytics é necessário. Instale com: pip install ultralytics")
        
        print(f"[INFO] Carregando modelo: {model_path}")
        
        # Carregar modelo (baixa automático se for nome padrão YOLO)
        try:
            self.model = YOLO(model_path, task='detect')
            print(f"[OK] Modelo carregado com sucesso!")
            print(f"[INFO] Tipo de modelo: {type(self.model)}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar modelo: {e}")
            raise
        
        # Configuração da câmera
        print(f"[INFO] Inicializando câmera {camera_id}")
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera {camera_id}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        
        # Configurações de detecção
        self.confidence = confidence
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.center_screen_x = frame_width // 2
        self.center_screen_y = frame_height // 2
        
        # Configurações de filtragem
        self.MIN_WIDTH = 20
        self.MAX_WIDTH = frame_width - 50
        self.MIN_HEIGHT = 20
        self.MAX_HEIGHT = frame_height - 50
        
        # Pular frames para aumentar FPS visual
        self.frame_skip = frame_skip
        self.frame_count = 0
        
        # Histórico de detecções
        self.last_boxes = []
        self.last_detections = []
        self.detection_count = 0
        
        print(f"[OK] Câmera inicializada com sucesso!")
        print(f"[INFO] Resolução: {frame_width}x{frame_height}")
        print(f"[INFO] Confiança: {confidence}")
        print(f"[INFO] Frame skip: {frame_skip}")

    def apply_size_filter(self, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Filtra caixas por tamanho para remover ruído."""
        filtered = []
        for (x1, y1, x2, y2) in boxes:
            width = x2 - x1
            height = y2 - y1
            
            if (self.MIN_WIDTH <= width <= self.MAX_WIDTH and
                self.MIN_HEIGHT <= height <= self.MAX_HEIGHT):
                filtered.append((x1, y1, x2, y2))
        
        return filtered

    def get_navigation_command(self, center_x: int, object_width: int) -> str:
        """Gera comando de navegação baseado na posição do objeto."""
        dead_zone = 50
        
        if object_width > 200:
            return "ALVO ALCANCADO - PARAR"
        
        error_x = center_x - self.center_screen_x
        
        if abs(error_x) < dead_zone:
            return "AVANCAR"
        elif error_x < 0:
            return f"<< ESQUERDA ({int(error_x)})"
        else:
            return f"DIREITA >> ({int(error_x)})"

    def get_statistics(self) -> dict:
        """Retorna estatísticas da detecção."""
        return {
            "frames_processados": self.frame_count,
            "deteccoes_totais": self.detection_count,
            "ultima_deteccao_count": len(self.last_boxes),
            "confianca_limiar": self.confidence
        }

    def save_config(self, output_file: str) -> None:
        """Salva configuração atual em arquivo JSON."""
        config = {
            "confidence": self.confidence,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "frame_skip": self.frame_skip,
            "min_width": self.MIN_WIDTH,
            "max_width": self.MAX_WIDTH,
            "min_height": self.MIN_HEIGHT,
            "max_height": self.MAX_HEIGHT,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"[OK] Configuração salva em: {output_file}")

    def load_config(self, config_file: str) -> None:
        """Carrega configuração de arquivo JSON."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.confidence = config.get("confidence", self.confidence)
            self.MIN_WIDTH = config.get("min_width", self.MIN_WIDTH)
            self.MAX_WIDTH = config.get("max_width", self.MAX_WIDTH)
            self.MIN_HEIGHT = config.get("min_height", self.MIN_HEIGHT)
            self.MAX_HEIGHT = config.get("max_height", self.MAX_HEIGHT)
            self.frame_skip = config.get("frame_skip", self.frame_skip)
            
            print(f"[OK] Configuração carregada de: {config_file}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar configuração: {e}")

    def run(self, show_stats: bool = True) -> None:
        """
        Executa o detector em tempo real.
        
        Controles:
            'q' - Sair
            's' - Salvar configuração
            'l' - Carregar configuração
            '+' - Aumentar confiança
            '-' - Diminuir confiança
            'h' - Mostrar ajuda
        """
        print("\n" + "="*60)
        print("DETECTOR DE OBJETOS COM MACHINE LEARNING")
        print("="*60)
        print("[INFO] Controles:")
        print("  'q' - Sair")
        print("  's' - Salvar configuração")
        print("  'l' - Carregar configuração")
        print("  '+' - Aumentar confiança (+0.05)")
        print("  '-' - Diminuir confiança (-0.05)")
        print("  'h' - Mostrar ajuda")
        print("="*60 + "\n")
        
        prev_time = time.time()
        fps = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERRO] Falha ao capturar frame")
                break
            
            self.frame_count += 1
            
            # Executar detecção a cada N frames
            if self.frame_count % (self.frame_skip + 1) == 0:
                try:
                    results = self.model(frame, conf=self.confidence, verbose=False)
                    result = results[0]
                    
                    self.last_boxes = []
                    self.last_detections = []
                    
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        width = x2 - x1
                        height = y2 - y1
                        
                        # Aplicar filtro de tamanho
                        if (width < self.MIN_WIDTH or width > self.MAX_WIDTH or
                            height < self.MIN_HEIGHT or height > self.MAX_HEIGHT):
                            continue
                        
                        self.last_boxes.append((x1, y1, x2, y2))
                        
                        # Extrair informações
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names.get(class_id, "Desconhecido")
                        
                        self.last_detections.append({
                            'bbox': (x1, y1, x2, y2),
                            'center': (center_x, center_y),
                            'width': width,
                            'height': height,
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': class_name
                        })
                    
                    self.detection_count += len(self.last_detections)
                
                except Exception as e:
                    print(f"[ERRO] Falha na detecção: {e}")
            
            # Desenhar detecções em todo frame (para fluidez)
            for detection in self.last_detections:
                x1, y1, x2, y2 = detection['bbox']
                center_x, center_y = detection['center']
                confidence = detection['confidence']
                class_name = detection['class_name']
                
                # Desenhar caixa
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Desenhar centro
                cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), -1)
                
                # Etiqueta com classe e confiança
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(
                    frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
            
            # Desenhar linha central
            cv2.line(
                frame,
                (self.center_screen_x, 0),
                (self.center_screen_x, self.frame_height),
                (255, 0, 0), 1
            )
            cv2.line(
                frame,
                (0, self.center_screen_y),
                (self.frame_width, self.center_screen_y),
                (255, 0, 0), 1
            )
            
            # FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            cv2.putText(
                frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )
            
            # Informações de detecção
            cv2.putText(
                frame, f"Confianca: {self.confidence:.2f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
            )
            
            cv2.putText(
                frame, f"Objetos: {len(self.last_detections)}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
            )
            
            if show_stats:
                cv2.putText(
                    frame, f"Frame: {self.frame_count}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1
                )
            
            cv2.imshow('ML Object Detector - Rover Vision', frame)
            
            # Controles
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n[INFO] Encerrando...")
                break
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                config_file = f"ml_config_{timestamp}.json"
                self.save_config(config_file)
            elif key == ord('l'):
                config_file = input("Nome do arquivo de configuração: ")
                self.load_config(config_file)
            elif key == ord('+'):
                self.confidence = min(1.0, self.confidence + 0.05)
                print(f"[INFO] Confiança aumentada para: {self.confidence:.2f}")
            elif key == ord('-'):
                self.confidence = max(0.0, self.confidence - 0.05)
                print(f"[INFO] Confiança diminuída para: {self.confidence:.2f}")
            elif key == ord('h'):
                print("\n[INFO] Controles:")
                print("  'q' - Sair")
                print("  's' - Salvar configuração")
                print("  'l' - Carregar configuração")
                print("  '+' - Aumentar confiança")
                print("  '-' - Diminuir confiança")
                print("  'h' - Mostrar ajuda\n")
        
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("ESTATÍSTICAS:")
        print(f"  Total de frames: {stats['frames_processados']}")
        print(f"  Total de detecções: {stats['deteccoes_totais']}")
        print(f"  FPS final: {int(fps)}")
        print("="*60)
        
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='Detector de objetos com Machine Learning para Rover',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Usar modelo YOLOv8 Nano (baixa automático)
  python MLModelConfig.py --model yolov8n.pt

  # Usar modelo customizado
  python MLModelConfig.py --model ./models/best.pt --confidence 0.7

  # Usar modelo TFLite
  python MLModelConfig.py --model best_int8.tflite --camera 0

  # Configuração completa
  python MLModelConfig.py --model yolov8s.pt --camera 0 --confidence 0.65 --width 640 --height 480
        """
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Caminho do modelo ou nome do modelo YOLO (ex: yolov8n.pt, best.pt)'
    )
    
    parser.add_argument(
        '--camera', '-c',
        type=int,
        default=0,
        help='ID da câmera a usar (padrão: 0)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.65,
        help='Limiar de confiança para detecções (0.0-1.0, padrão: 0.65)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=640,
        help='Largura do frame (padrão: 640)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=480,
        help='Altura do frame (padrão: 480)'
    )
    
    parser.add_argument(
        '--frame-skip',
        type=int,
        default=2,
        help='Número de frames a pular (padrão: 2)'
    )
    
    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Não mostrar estatísticas em tempo real'
    )
    
    args = parser.parse_args()
    
    try:
        detector = MLObjectDetector(
            model_path=args.model,
            camera_id=args.camera,
            confidence=args.confidence,
            frame_width=args.width,
            frame_height=args.height,
            frame_skip=args.frame_skip
        )
        
        detector.run(show_stats=not args.no_stats)
        
    except KeyboardInterrupt:
        print("\n[INFO] Interrupção do usuário")
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
