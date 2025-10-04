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
 ***

## Uso

1. Instalar dependências:
```bash
  sudo apt install -y python3-picamera2
  sudo apt install -y python3-opencv 
```

2. Clone o repositório com os drivers:
````bash
git clone "https://github.com/AbstractGleidson/Rover.git"
````

3. Navegue para a pasta dos drivers de câmera:
````bash
cd Rover/driver_camera
````
4. Execute os programas com privilégios de root

    4.1 - Captura simples com a câmera
   ````bash
   sudo python3 src/captura_imagem_simples.py
   ````
   4.2 - Captura em tempo de execução
   ````bash
   sudo python3 src/captura_imagem_tempo_de_execução.py
   ````
   4.3 - Captura não volátil de imagem
   ````bash
   sudo python3 src/captura_imagem_salvar.py
   ````
---
