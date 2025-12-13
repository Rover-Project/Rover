"""
MLModelConfig - Detector de objetos portável com suporte a múltiplos modelos
Suporta: YOLO, TensorFlow Lite
"""

import cv2
import numpy as np
import os
import time
from pathlib import Path


class MLModelConfig:
    """Classe unificada para detecção de objetos com diferentes modelos ML"""
    
    def __init__(self, model_path, model_type='auto', camera_id=0, confidence=0.5):
        """
        Args:
            model_path: Caminho completo ou relativo ao modelo
            model_type: 'yolo', 'tflite' ou 'auto' (detecta pela extensão)
            camera_id: ID da câmera (0 = padrão)
            confidence: Threshold de confiança (0.0-1.0)
        """
        self.model_path = self._resolve_model_path(model_path)
        self.model_type = self._detect_model_type(model_type)
        self.model = None
        self.cap = cv2.VideoCapture(camera_id)
        
        # Configurações
        self.confidence = confidence
        self.min_width = 20
        self.max_width = 30000
        self.frame_skip = 0
        self.frame_count = 0
        
        self._load_model()
    
    def _resolve_model_path(self, model_path):
        """Resolve caminho relativo ou absoluto do modelo"""
        path = Path(model_path)
        
        if path.is_absolute():
            return str(path)
        
        # Tenta no diretório atual
        if path.exists():
            return str(path.absolute())
        
        # Tenta em ./models/
        models_dir = Path(__file__).parent / 'models' / model_path
        if models_dir.exists():
            return str(models_dir)
        
        # Tenta em ../../../models/
        relative_models = Path(__file__).parent.parent / 'models' / model_path
        if relative_models.exists():
            return str(relative_models)
        
        raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
    
    def _detect_model_type(self, model_type):
        """Detecta tipo de modelo pela extensão"""
        if model_type != 'auto':
            return model_type.lower()
        
        ext = Path(self.model_path).suffix.lower()
        if ext == '.tflite':
            return 'tflite'
        elif ext in ['.pt', '.onnx']:
            return 'yolo'
        
        return 'tflite'
    
    def _load_model(self):
        """Carrega o modelo apropriado"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Arquivo não existe: {self.model_path}")
        
        print(f"[+] Carregando modelo {self.model_type.upper()}: {self.model_path}")
        
        if self.model_type == 'yolo':
            self._load_yolo()
        elif self.model_type == 'tflite':
            self._load_tflite()
        
        # Configuração da câmera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[+] Câmera configurada 640x480")
    
    def _load_yolo(self):
        """Carrega modelo YOLO"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path, task='detect')
            print("[+] YOLO carregado com sucesso")
        except ImportError:
            raise ImportError("YOLO não instalado. Execute: pip install ultralytics")
    
    def _load_tflite(self):
        """Carrega modelo TensorFlow Lite"""
        Interpreter = None
        
        try:
            from tflite_runtime.interpreter import Interpreter
            print("[+] Usando tflite-runtime")
        except ImportError:
            try:
                import tensorflow as tf
                Interpreter = tf.lite.Interpreter
                print("[+] Usando TensorFlow")
            except ImportError:
                raise ImportError("Instale 'tensorflow' ou 'tflite-runtime'")
        
        try:
            self.model = Interpreter(model_path=self.model_path)
            self.model.allocate_tensors()
            print("[+] TFLite carregado com sucesso")
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar TFLite: {e}")
    
    def detect(self, frame):
        """Detecta objetos no frame. Retorna: [(x1, y1, x2, y2, conf, class_id), ...]"""
        if self.model_type == 'yolo':
            return self._detect_yolo(frame)
        elif self.model_type == 'tflite':
            return self._detect_tflite(frame)
        return []
    
    def _detect_yolo(self, frame):
        """Detecção YOLO"""
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []
        
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            
            width = int(x2 - x1)
            if self.min_width <= width <= self.max_width:
                detections.append((int(x1), int(y1), int(x2), int(y2), conf, cls_id))
        
        return detections
    
    def _detect_tflite(self, frame):
        """Detecção TensorFlow Lite com YOLOv8"""
        h_orig, w_orig = frame.shape[:2]
        input_details = self.model.get_input_details()
        output_details = self.model.get_output_details()
        
        # Preparação da imagem
        input_shape = input_details[0]['shape']
        input_h, input_w = input_shape[1], input_shape[2]
        dtype = input_details[0]['dtype']
        
        resized = cv2.resize(frame, (input_w, input_h))
        
        # Normalização (int8 vs float32)
        if dtype == np.int8 or dtype == np.uint8:
            input_data = np.expand_dims(resized, axis=0).astype(dtype)
        else:
            input_data = np.expand_dims(resized, axis=0).astype(np.float32) / 255.0
        
        # Inferência
        self.model.set_tensor(input_details[0]['index'], input_data)
        self.model.invoke()
        
        detections = []
        
        # Processamento de saída
        if len(output_details) == 1:
            output_data = self.model.get_tensor(output_details[0]['index'])[0]
            output_data = output_data.T  # Shape: (N, 4 + num_classes)
            
            boxes_xywh = []
            confidences = []
            class_ids = []
            
            for row in output_data:
                classes_scores = row[4:]
                max_score = np.max(classes_scores)
                
                if max_score > self.confidence:
                    cx, cy, w_box, h_box = row[0:4]
                    class_id = np.argmax(classes_scores)
                    
                    # Conversão para coordenadas do frame original
                    x1 = int((cx - w_box/2) * (w_orig / input_w))
                    y1 = int((cy - h_box/2) * (h_orig / input_h))
                    x2 = int((cx + w_box/2) * (w_orig / input_w))
                    y2 = int((cy + h_box/2) * (h_orig / input_h))
                    
                    # Validação de limites
                    x1 = max(0, min(x1, w_orig - 1))
                    y1 = max(0, min(y1, h_orig - 1))
                    x2 = max(0, min(x2, w_orig))
                    y2 = max(0, min(y2, h_orig))
                    
                    boxes_xywh.append([x1, y1, x2 - x1, y2 - y1])
                    confidences.append(float(max_score))
                    class_ids.append(int(class_id))
            
            # NMS
            if len(boxes_xywh) > 0:
                indices = cv2.dnn.NMSBoxes(boxes_xywh, confidences, self.confidence, 0.45)
                if len(indices) > 0:
                    for i in indices.flatten():
                        x, y, w, h = boxes_xywh[i]
                        detections.append((x, y, x + w, y + h, confidences[i], class_ids[i]))
        
        return detections
    
    def run(self, window_name="ML Object Detection"):
        """Executa detecção em tempo real"""
        print("\n[*] Iniciando captura. Pressione 'q' para sair.\n")
        
        last_detections = []
        last_command = "AGUARDANDO..."
        prev_time = time.time()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[!] Erro ao capturar frame")
                break
            
            self.frame_count += 1
            
            # Processa frame a cada N frames
            if self.frame_count % (self.frame_skip + 1) == 0:
                last_detections = self.detect(frame)
                

            
            # Desenha detecções
            for x1, y1, x2, y2, conf, cls_id in last_detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # FPS (corrigido)
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time + 1e-6)
            prev_time = curr_time
            
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, last_command, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, f"Modelo: {self.model_type.upper()} | Conf: {self.confidence}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("[+] Captura finalizada.\n")
    
    def close(self):
        """Libera recursos"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()