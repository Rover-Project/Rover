# Integração da Câmera IMX219 (8MP) – Modelo C3762 no Raspberry Pi 5

Este guia demonstra como integrar e configurar a câmera IMX219 de 8 megapixels (modelo C3762) no Raspberry Pi 5, incluindo instalação de drivers, testes de funcionamento e captura de imagens.

---

## Especificações da Câmera Utilizada

| Especificação     | Detalhes                                |
| ------------------|-----------------------------------------|
| Modelo            | C3762 (SHCHV)                           |
| Sensor            | Sony IMX219                             |
| Resolução         | 8 MP (3280 × 2464 pixels)               | 
| Compatibilidade   | Raspberry Pi 5 (conector CSI)           |
| Campo de visão    | 77° / 130° / 220° (dependendo da lente) |
| Tamanho do módulo | 25 × 24 mm                              |
| Peso aproximado   | 3 g                                     |
  


- **Observação:** o IMX219 é o mesmo sensor usado no Raspberry Pi Camera Module V2, já amplamente testado e documentado.

***

## Procedimentos de Instalação

   **1. Desligar o Raspberry Pi 5**

   **2. Descarregar a energia estática do corpo (Toque numa torneira metálica por alguns segundos; Estrutura metálica aterrada; Pulseira antiestática)**

   **3. Conectar o cabo flat da câmera ao conector CSI (lado dos contatos voltado para a porta HDMI)**

   **4. Fixar o cabo no conector pressionando a trava**

   **5. Vídeo prático de instalação: [Assista-me](https://youtu.be/GImeVqHQzsE)**

***

## Configuração de Software

**1. Atualizar o sistema:**
````bash
sudo apt update 
sudo apt full-upgrade
````


 **2. Instalar dependências:**
````bash
sudo apt install -y python3-picamera2
sudo apt install -y python3-opencv 
````

**3. Teste de reconhecimento da câmera:**
````bash
rpicam-hello --list-cameras

# A flag --list-cameras mostra todas as câmeras detectadas pelo sistema,
# com informações como o modelo, a resolução e o número do dispositivo (cam0, cam1 etc).

````

**4. Forçando o reconhecimento manualmente:**

- Em alguns casos a câmera não é automaticamente detectada pela Raspberry Pi, sendo necessário editar o arquivo config.txt da Raspberry Pi para forçar o reconhecimento manual do sensor.

````bash
# Acesse o arquivo config.txt da Raspberry Pi

sudo nano /boot/config.txt

# Dentro do arquivo config.txt adicione as linhas de comando a seguir (de preferência no final do arquivo):

camera_auto_detect=0
dtoverlay=imx219,cam0

# O parâmetro "imx219" indica o sendor de imagem da câmera, e o mesmo deve ser modificado dependendo da câmera que estiver sendo utilizada
# por exemplo (imx477, ov5647, imx519, etc.):

dtoverlay=<nome_do_sensor>,cam0

# O parâmetro "cam0" indica que a câmera está conectada à porta CSI0, caso estivesse na porta CSI1, deve ser usado:

dtoverlay=<nome_do_sensor>,cam1
 ````

## Uso

1. Clone o repositório com os drivers:
````bash
git clone "https://github.com/AbstractGleidson/Rover.git"
````

2. Navegue para a pasta dos drivers de câmera:
````bash
cd Rover/driver_camera
````
3. Execute os programas com privilégios de root

    3.1 - Captura simples com a câmera
   ````bash
   sudo python3 src/captura_imagem_simples.py
   ````
   3.2 - Captura em tempo de execução
   ````bash
   sudo python3 src/captura_imagem_tempo_de_execucao.py
   ````
   3.3 - Captura não volátil de imagem
   ````bash
   sudo python3 src/captura_imagem_salvar.py
   ````
---
