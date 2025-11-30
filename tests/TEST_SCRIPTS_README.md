# 🧪 Scripts de Teste Simplificados - MediaPipe

Pasta com scripts simplificados para teste inicial dos modelos MediaPipe em segmentos específicos:
- **Detecção de Gestos** (Gesture Recognition)
- **Mapeamento de Mãos** (Hand Landmarks)
- **Detecção de Objetos** (Object Detection)

## 📋 Pré-requisitos

### Arquivos de Modelo Necessários

Os scripts requerem os seguintes arquivos `.task` nesta pasta:

```
tests/
├── gesture_recognizer.task      # Modelo para reconhecimento de gestos
├── hand_landmarker.task         # Modelo para mapeamento de pontos de mão
├── test_gesture_recognition.py
├── test_hand_landmarks.py
├── test_object_detection.py
└── requirements.txt
```

**Para baixar os modelos**, acesse:
- [MediaPipe Model Hub](https://developers.google.com/mediapipe/solutions/model_hub)
- Ou use os modelos já na pasta se já foram baixados

### Instalação de Dependências

```bash
# Navegue até a pasta tests
cd Rover/tests

# Instale as dependências
pip install -r requirements.txt
```

## 🎯 Scripts de Teste

### 1. Reconhecimento de Gestos
**Arquivo:** `test_gesture_recognition.py`

Detecta gestos das mãos em tempo real:
- Thumbs Up (Polegar para cima)
- Thumbs Down (Polegar para baixo)
- Pointing Up (Apontando para cima)
- Victory (Sinal de vitória)
- Open Palm (Palma aberta)
- Closed Fist (Punho fechado)

**Uso:**
```bash
python test_gesture_recognition.py
# ou com câmera específica
python test_gesture_recognition.py --camera-id 0
```

**Controles:**
- `q` - Sair
- `s` - Capturar screenshot

**Saída:**
- Mostra o gesto detectado com confiança (0-1)
- Exibe FPS em tempo real
- Salva screenshots ao pressionar `s`

---

### 2. Mapeamento de Pontos de Mão
**Arquivo:** `test_hand_landmarks.py`

Detecta os 21 pontos de referência (landmarks) das mãos:
- Pulso (wrist)
- Palma (palm)
- Dedos e articulações

**Uso:**
```bash
python test_hand_landmarks.py
# ou com múltiplos parâmetros
python test_hand_landmarks.py --camera-id 0 --num-hands 2
```

**Parâmetros:**
- `--camera-id` - ID da câmera (padrão: 0)
- `--num-hands` - Número máximo de mãos a detectar (padrão: 2)

**Controles:**
- `q` - Sair
- `s` - Capturar screenshot

**Saída:**
- Desenha os 21 pontos de referência por mão
- Mostra conexões entre pontos
- Identifica se é mão esquerda ou direita com confiança
- Exibe FPS em tempo real

---

### 3. Detecção de Objetos
**Arquivo:** `test_object_detection.py`

Detecta objetos por segmentação de cor HSV + forma (círculos):

**Cores suportadas:**
- `red` - Vermelho (padrão)
- `blue` - Azul
- `green` - Verde
- `yellow` - Amarelo

**Uso:**
```bash
python test_object_detection.py
# ou com parâmetros customizados
python test_object_detection.py --camera-id 0 --color red --min-radius 10 --max-radius 200
```

**Parâmetros:**
- `--camera-id` - ID da câmera (padrão: 0)
- `--color` - Cor do objeto (padrão: red)
- `--min-radius` - Raio mínimo em pixels (padrão: 10)
- `--max-radius` - Raio máximo em pixels (padrão: 200)

**Controles:**
- `q` - Sair
- `s` - Capturar screenshot
- `c` - Ativar/desativar modo calibração (mostra valores HSV)

**Saída:**
- Detecta círculos na imagem
- Mostra duas janelas:
  - Detecção (com círculos desenhados)
  - Máscara HSV (para visualizar a segmentação)
- Exibe raio e posição dos objetos detectados
- FPS em tempo real

---

## 🔧 Modo Calibração (Detecção de Objetos)

Se o script não detectar bem sua cor, use o modo calibração:

```bash
python test_object_detection.py --color red
# Pressione 'c' durante a execução para ativar modo calibração
```

**No modo calibração:**
- Um círculo aparecerá no centro da tela
- Alinhe o objeto com o círculo
- Veja os valores HSV do pixel central
- Ajuste os intervalos em `COLOR_RANGES` se necessário

**Exemplo de ajuste:**
```python
'red': [
    ((0, 100, 100), (10, 255, 255)),      # Vermelho inferior
    ((160, 100, 100), (180, 255, 255))    # Vermelho superior
]
```

---

## 📊 Estrutura dos Scripts

Todos os scripts seguem o padrão:

```python
class [Nome]Test:
    def __init__(self, ...):
        # Inicializa configurações
        
    def _load_model(self):
        # Carrega modelo .task
        
    def run(self):
        # Loop principal de captura/processamento
        
def main():
    # Parse de argumentos CLI
```

---

## 🐛 Troubleshooting

### Câmera não abre
```bash
# Teste qual ID usar
python -c "import cv2; cap = cv2.VideoCapture(1); print('OK' if cap.isOpened() else 'FAIL')"
# Tente --camera-id 0, 1, 2, etc
```

### Modelos não encontrados
Garanta que estão na pasta `tests/`:
```bash
ls -la *.task
# Deve exibir:
# gesture_recognizer.task
# hand_landmarker.task
```

### Baixo FPS / Lag
- Reduza a resolução da câmera
- Feche outras aplicações
- Teste em máquina com melhor GPU

### Detecção imprecisa (Gestos/Landmarks)
- Teste em boa iluminação
- Use fundo simples
- Aumentar confiança é feito nos parâmetros do modelo

### Detecção de objetos imprecisa
1. Use modo calibração (`c`)
2. Ajuste cores em `COLOR_RANGES`
3. Varie `--min-radius` e `--max-radius`
4. Melhore a iluminação

---

## 📝 Logs e Saída

Os scripts exibem:
- ✓ Status de inicialização
- ✓ FPS em tempo real
- ✓ Detecções com confiança
- ✓ Mensagens de captura de screenshot
- ✓ Mensagens de erro se houver

---

## 🚀 Próximos Passos

Após validar os modelos com estes scripts:

1. **Integrar ao Rover:** Use as classes em `rover_lib/modules/vision/`
2. **Controlar movimentos:** Mapear gestos para comandos do rover
3. **Processar em tempo real:** Executar em Raspberry Pi com camera module

---

## 📚 Referências

- [MediaPipe Official Docs](https://developers.google.com/mediapipe)
- [MediaPipe Solutions](https://developers.google.com/mediapipe/solutions)
- [OpenCV Documentation](https://docs.opencv.org/)

