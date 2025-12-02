# __1. INTRODUÇÃO__
Esse guia contém o passo a passo de como preparar a API de detecção de objetos do __TensorFlow Lite Runtime__ para otimizar o desempenho em uma Raspberry Pi 5. 

O guia cobre os seguintes passos:

1. Instalar o TensorFlow Life Runtime;
2. Instalar o OpenCV;
3. Configurar o diretório e baixar o modelo otimizado;
4. Configuração do diretório e download do modelo otimizado;
5. Detecção dos objetos na prática;
6. Referências.


O guia foi escrito pensando no TensorFlow Lite rodando em uma Raspberry Pi 5.

# __2. Instalar o TensorFlow Lite Runtime__
Primeiro, devemos instalar o TensorFlow Lite Runtime para máxima eficiência. Execute o seguinte comando:

```bash
pip3 install tflite-runtime
```

O TensorFlow e suas dependências precisam da "LibAtlas package" para otimizar operações numéricas. Instale-a:

```bash
sudo apt-get install libatlas-base-dev
```
O projeto requisita algumas dependências adicionais:

```bash
sudo pip3 install pillow lxml jupyter cython
sudo apt-get install python-tk
```
Isso é tudo o necessário para o TensorFlow. O próximo passo é configurar o OpenCV.

# __3. Instale o OpenCV__
Para processamento de imagens, captura de frames da câmera e desenho das caixas delimitadores, utilizaremos o **OpenCV**.

Para fazer o OpenCV funcionar na Raspberry, precisamos de algumas dependências. Baixe-as:

```bash
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
```
```bash
sudo apt-get install libavcodec-dev libavformat-dev libswscale libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install qt4-dev-tools libatlas-base-dev 
```

Com todas essas instaladas, podemos ir para o OpenCV: 

```bash
sudo pip3 install opencv-python
```

O OpenCV está instalado e funcional. 
    
# __4. Configuração do diretório e Download do Modelo Otimizado__ 
Agora que temos todas as dependências instaladas, devemos definir o diretório do TensorFlow Lite. Crie e se mova para o diretório tensorflow1 com os seguintes comandos: 

```bash
mkdir tensorflow1
cd tensorflow1
```

O fluxo TFLite requer apenas o modelo otimizado (.tflite) e o arquivo de rótulos(.txt ou .pbtxt). Baixe o modelo "SSDLite-MobileNet V2" e o arquivo de rótulos (Labels) com os seguintes comandos:

```bash
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/object_detection/ssd_mobilenet_v2_320x320_coco_tf2_20200714.tflite

wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/object_detection/labelmap.txt
```

Agora o modelo e as Labels estão no diretório "tensorflow1" e prontos para serem usados.

# __5. Realize as detecções__
Bom, agora que tudo está configurado, vamos ao script. O código (object_detection_picamera2.py) basicamente: define os caminhos para o modelo e para o label map (dict com as classes dos objetos capturados), carrega o modelo na memória da Raspberry, inicializa a câmera e performa a captura, pré-processamento, detecção, pós-processamento e exibição dos objetos identificados pelo modelo em cada frame gerado pela Picamera2.

Pelo poder de processamento da Raspberry Pi e quão pesado é o processo de detecção, sugere-se o uso de baixas resoluções. 
    
O modelo SSD mobileNet V2 que foi baixado foi otimizado para __320 x 320__. (resolução ideal para melhor desempeho).

P.S. Testar 640 x 480. Outra resolução recomendada, mas resultará num FPS mais baixo.

Abra o terminal e execute no diretório onde o script foi carregado:

```bash
python3 object_detection.py
```
    
Uma vez que o script foi iniciado, você verá, em tempo real, a câmera e boxes delimitando os objetos identificados. 

OBS: O script, com pequenas modificações, também suporta a detecção de objetos com câmeras USB. 

# __6. Referências__ 

https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi?tab=readme-ov-file#2-install-tensorflow