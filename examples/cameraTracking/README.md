# CameraTracking

A câmera do Rover acompanha um objeto vermelho movendo os dois servos do suporte pan-tilt. As rodas não se movem.

## Hardware

- Câmera (Picamera2 ou webcam)
- PCA9685 (I²C, endereço `0x40`) com:
  - **PAN** (horizontal): servo de rotação contínua (360°) no canal 0
  - **TILT** (vertical): servo de 180° no canal 1

No PC, os servos são simulados (os comandos aparecem no terminal) e a imagem vem da webcam.

## Execução

```bash
cd examples/cameraTracking
python main.py
```

Na janela da imagem: `q` encerra e `c` centraliza a câmera.

## Como funciona

1. `ProcessingImage.color_segmentation()` gera uma máscara com as regiões vermelhas.
2. Os **momentos** da máscara (`cv2.moments`) dão a área e o centro do objeto.
3. O erro é a distância do objeto ao centro da imagem, normalizada entre -1 e 1.
4. Os dois servos corrigem esse erro de formas diferentes:
   - **PAN (360°)** é controlado por velocidade: o erro define a **velocidade** do giro (`pan(kp_pan * erro_x)`). Perto do centro, dentro da `deadzone`, o giro para. O `PanTilt` estima a posição do PAN e o para nos limites `pan.min`/`pan.max`, protegendo o cabo da câmera.
   - **TILT (180°)** tem posição: a cada frame, o **ângulo** anda um pouco na direção do objeto (`tilt_up(-kp_tilt * erro_y)`), respeitando os limites `min` e `max`.

É um exemplo de **controle proporcional**: quanto mais longe do centro, mais forte a correção.

## Ajustes (`config.yaml`)

| Parâmetro | Efeito |
|---|---|
| `tracking.kp_pan` | Velocidade do PAN com o objeto na borda. Muito alto: a câmera oscila; muito baixo: perde o objeto |
| `tracking.kp_tilt` | Graus por frame do TILT com o objeto na borda |
| `tracking.deadzone` | Região central em que a câmera fica parada (evita tremer) |
| `tracking.min_area` | Tamanho mínimo da região vermelha para ser considerada um objeto |
| `pan_tilt.pan.trim` | Corrige o PAN girando sozinho quando deveria estar parado |
| `pan_tilt.pan.invert` / `pan_tilt.tilt.invert` | Invertem o sentido, se a câmera fugir do objeto em vez de segui-lo |
| `pan_tilt.pan.min` / `max` | Limites do giro do PAN, em graus (0 = frente), para não forçar o cabo flat |
| `pan_tilt.tilt.min` / `max` | Limites do TILT para não forçar o suporte |
