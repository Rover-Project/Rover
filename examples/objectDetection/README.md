# **_DOCUMENTAÇÃO - USO DO YOLOV8n PARA DETECÇÃO DE OBJETOS_**

## **_INTRODUÇÃO_**

Neste script, utilizamos o modelo **YOLOV8n** a partir da lib **ultralytics** para uma detecção em tempo real de um objeto no campo de visão da câmera e sua posição.

## **_SOBRE O SCRIPT_**

### IMPORTS E VARIÁVEIS GLOBAIS:

Inicia configurando as câmeras com seus parâmetros padrões.

Logo em seguida, carrega o modelo utilizando a sua importação direta a partir da lib **ultralytics**:

```python
model = YOLO("yolov8n.pt")

model.export(format="ncnn")
```

### MAIN:

Logo no ínicio do main, iniciamos um loop infinito e adquirimos os frames providos da câmera.

A operação de inferência do modelo **YOLOv8** acontece na seguinte linha:

```python
results = model(frame, conf=0.5)
```

Todo o código a partir disso consiste no cálculo do fps e desenho das informações adquiridas na inferência no frame exibido.

## **_EXECUTANDO O SCRIPT_**:

### INSTALAÇÃO DE LIBS ESPECÍFICAS:

Por conta das enormes libs requisitadas na instalação, tentar baixar o ultralytics diretamente em um sistema operacional Linux (Como a Raspberry Pi5) não é possível. Rode os seguintes comandos no terminal da Rasp:

1. Garanta que Rasp e python estejam plenamente atualizadas:

```bash
sudo apt update
sudo apt install build-essential python3-dev
```

2. Para a compilação do SciPy na Rasp, precisamos baixar a lib gfortran:

```bash
sudo apt install gfortran
```

3. Para cálculos de algebra linear de alta performance executados pelo SciPy e pelo numpy, precisamos das libs **openblas** e **lapack**:

```bash
sudo apt install libopenblas-dev liblapack-dev
```

4. Para evitar erros do SSL, instalamos gerenciadores de Build do próprio sistema:

```bash
sudo apt install cmake ninja-build
```

5. Por fim, instale algumas libs de visão computacional requisitadas pelo openCV para que não vem instaladas por padrão:

```bash
sudo apt install libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev
```

### INSTALANDO O ULTRALYTICS:

Finalmente, rode o comando para instalar o ultralytics:

```bash
pip install ultralytics
```

### EXECUTANDO O SCRIPT

Com a câmera devidamente conectada a Rasp, partindo da raiz do projeto, execute o seguinte comando:

```bash
python -m examples.objectDetection.main
```
