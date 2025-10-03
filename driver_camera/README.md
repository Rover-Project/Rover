# *Integração da Câmera IMX219 (8MP) – Modelo C3762 no Raspberry Pi 5*

1. **Especificações da Câmera Utilizada:**

   **1.1 - Modelo: C3762 (SHCHV)**

   **1.2  - Sensor: Sony IMX219**

   **1.3 - Resolução: 8 MP (3280 × 2464 pixels)**

   **1.4 - Compatibilidade: Raspberry Pi 5 (conector CSI)**

   **1.5 - Campo de visão: 77° / 130° / 220° (dependendo da lente)**

   **1.6 - Tamanho do módulo: 25 × 24 mm**

   **1.7 - Peso aproximado: 3 g**

- **Observação:** o IMX219 é o mesmo sensor usado no Raspberry Pi Camera Module V2, já amplamente testado e documentado.

***

2. **Procedimentos de Instalação**

   **2.1 - Desligar o Raspberry Pi 5**

   **2.2 - Descarregar a energia estática do corpo (Toque numa torneira metálica por alguns segundos; Estrutura metálica aterrada; Pulseira antiestática)**

   **2.3 - Conectar o cabo flat da câmera ao conector CSI (lado dos contatos voltado para a porta HDMI)**

   **2.4 - Fixar o cabo no conector pressionando a trava**

   **2.5 - Vídeo prático de instalação: [Assista-me](https://youtu.be/GImeVqHQzsE)**

***

3. **Configuração de Software**

   **3.1 - Atualizar o sistema:**

    ````
    bash

       sudo apt update 
       sudo apt full-upgrade
    ````
    **3.2 - Verificar se a câmera foi detectada:**
     ````
    bash

        rpicam-hello
     ````
 ****

4. **Exemplo Prático**

   **4.1 - Instalar dependências:**

   ````
    bash

        sudo apt install -y python3-picamera2
        sudo apt install -y python3-opencv 
   ````
   ***
   **4.2 - Captura simples com a câmera:**

   ```python
    from picamera2 import Picamera2
    import cv2

    # Inicializa a câmera
    picam2 = Picamera2()

    # Configura a resolução
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)

    # Inicia captura
    picam2.start()

    # Captura uma imagem
    frame = picam2.capture_array()

    # Mostra a imagem capturada
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("Imagem Capturada", frame_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Resultado esperado: O código deve abrir uma janela com a imagem capturada pela câmera. Se aparecer, está tudo certo com a instalação e configuração do software.
   ``` 
   ***
   **4.3 - Captura em loop em tempo de execução**

   ````python
    from picamera2 import Picamera2
    import cv2

    # Inicializa a câmera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    while True:
        # Captura um frame (imagem atual da câmera)
        frame = picam2.capture_array()

        # Mostra na tela
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Camera em Loop", frame_bgr)

        # Sai se apertar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    # O resultado esperado é a visualização de um vídeo ao vivo, com baixa latência, que permanece em execução até que o usuário pressione a tecla q para encerrar.
   ````
   ***

   **4.4 - Processamento com OpenCV – Detecção de Bordas (Canny)**

   ````python
    from picamera2 import Picamera2
    import cv2

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    while True:
        frame = picam2.capture_array()

        # Converte para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Aplica detecção de bordas (Canny)
        edges = cv2.Canny(gray, 100, 200)

        # Mostra resultado
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Camera Original", frame_bgr)
        cv2.imshow("Deteccao de Bordas", edges)

        # Pressione 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    # Resultado esperado: O código deve abrir duas janelas, uma com a imagem original da câmera e outra mostrando apenas as bordas detectadas.
   ````
   ***

    **4.5 - Processamento com OpenCV – Detecção de Rostos**

     ````python
    from picamera2 import Picamera2
    import cv2

    # Carrega o classificador pré-treinado do OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta rostos
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Desenha retângulos ao redor dos rostos
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Deteccao de Rostos", frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    # Resultado esperado: O código deve identificar a presença de rostos na câmera e desenhar um retângulo verde em volta do rosto detectado.
    ````
    ***
    **4.6 - Captura não volátil de imagem**
    ````python
    from picamera2 import Picamera2, Preview
    import time

    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()

    picam2.configure(camera_config)
    picam2.start_preview(Preview.QTGL)

    picam2.start()
    time.sleep(2)
    picam2.capture_file("test.jpg")

    # Resultado esperado: O código deve capturar uma imagem dois segundos após a inicialização da câmera (para permitir o foco) e salvará em um arquivo chamado "teste.jpg".
    ````
    ***
    **4.7 - Captura não volátil de vídeo**

    ````python
    from picamera2 import Picamera2
    picam2 = Picamera2()
    picam2.start_and_record_video("test.mp4", duration=5)

    # Resultado esperado: O código deve capturar um vídeo de cinco segundos de duração e salvá-lo em um arquivo chamado "test.mp4".
    ````
    ***
