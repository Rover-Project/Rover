# Guia de Montagem e Conexões Elétricas: Robô Rover

Este tutorial destina-se a orientar a montagem e interligação de todos os componentes eletrônicos do robô móvel baseado em **Raspberry Pi 5**.

---

## 1. Visão Geral da Arquitetura de Alimentação

O robô utiliza um sistema de **alimentação dupla e isolada** para evitar que o ruído gerado pelos motores cause reinicializações na Raspberry Pi:

* **Linha de Controle/Lógica:** Alimentada exclusivamente por um **Powerbank de 10.000 mAh** via porta USB Type-C na Raspberry Pi 5.
* **Linha de Potência (Motores):** Alimentada por um **Case de 6x Pilhas AA (8.5V/9V)** dedicado para a Ponte-H L298N e para a alimentação dos Servos no PCA9685.

* **Terra Comum (GND):** Todos os GNDs do sistema (Raspberry Pi, Ponte-H, PCA9685 e Bateria) devem estar interligados para garantir a correta referência dos sinais de controle.

---

## 2. Mapeamento das Conexões da GPIO (Raspberry Pi 5)

### 2.1. Ponte-H L298N (Controle dos Motores DC)
Responsável pelo controle de velocidade e sentido de rotação dos dois motores DC de 9V.

| Pino da Ponte-H | Função / Descrição | Pino Físico (Raspberry Pi 5) | Nome Lógico (GPIO) |
| :--- | :--- | :--- | :--- |
| **IN1** | Entrada de Sinal 1 | **Pino 29** | GPIO 5 |
| **IN2** | Entrada de Sinal 2 | **Pino 31** | GPIO 6 |
| **IN3** | Entrada de Sinal 3 | **Pino 32** | GPIO 12 |
| **IN4** | Entrada de Sinal 4 | **Pino 33** | GPIO 13 |
| **GND** | Referência de Terra | **Pino 34** | GND |

**Conexões de Potência da Ponte-H:**
* **12V / VCC:** Ligado ao pólo **Positivo (+)** do Case de Pilhas (8.5V).
* **GND:** Ligado ao pólo **Negativo (-)** do Case de Pilhas e derivado para a Raspberry Pi (Pino 34).
* **OUT1 / OUT2:** Ligados aos terminais do **Motor DC Esquerdo**.
* **OUT3 / OUT4:** Ligados aos terminais do **Motor DC Direito**.

---

### 2.2. Módulo PCA9685 (Controlador PWM / Servos)
Comunica-se com a Raspberry Pi via barramento **I2C** para controlar os Servo Motores de 360°.

| Pino do PCA9685 | Função / Descrição | Pino Físico (Raspberry Pi 5) | Nome Lógico (GPIO) |
| :--- | :--- | :--- | :--- |
| **VCC** | Alimentação Lógica (3.3V / 5V) | **Pino 4** | 5V Power |
| **SDA** | Dados I2C | **Pino 3** | GPIO 2 (SDA) |
| **SCL** | Clock I2C | **Pino 5** | GPIO 3 (SCL) |
| **GND** | Referência de Terra | **Pino 6** | GND |

**Conexões de Potência e Servos no PCA9685:**
* **V+ (Terminal):** Conectado ao pino de saída **5V da Ponte-H** para fornecer corrente para os servos sem sobrecarregar a placa lógica.
* **GND (Terminal):** Referência de Terra comum a todo o sistema. 
* **Canais PWM (0 e 1):** Conectar os cabos de 3 pinos dos Servo Motores.

---

### 2.3. Sensor LiDAR TF-Luna (Sensor de Distância)
Comunica-se via interface de comunicação serial **UART**.

| Pino do LiDAR TF-Luna | Função / Descrição | Pino Físico (Raspberry Pi 5) | Nome Lógico (GPIO) |
| :--- | :--- | :--- | :--- |
| **VCC** | Alimentação do Sensor | **Pino 2** | 5V Power |
| **GND** | Referência de Terra | **Pino 9** | GND |
| **RX** | Recepção de Dados (Serial) | **Pino 8** | GPIO 14 (UART TX) |
| **TX** | Transmissão de Dados (Serial) | **Pino 10** | GPIO 15 (UART RX) |

**Comunicação Serial (UART):** A conexão é cruzada. O pino **RX do LiDAR** conecta no pino **TX da Raspberry Pi**, e o pino **TX do LiDAR** conecta no pino **RX da Raspberry Pi**.

---

## 3. Passo a Passo do Processo de Montagem

1. **Alimentação:** Conecte o cabo USB-C do Powerbank na Raspberry Pi 5, mas mantenha-o desligado.
2. **Infraestrutura I2C:** Ligue o módulo PCA9685 nos pinos 3, 4, 5 e 6 da Raspberry Pi.
3. **Driver de Motores:** Ligue as entradas IN1-IN4 da Ponte-H nos pinos 29, 31, 32 e 33 da Raspberry Pi.
4. **Sensor Lidar:** Conecte os pinos TX/RX nos pinos 8 e 10, e a alimentação 5V/GND nos pinos 2 e 9.
5. **Verificação de GND:** Confirme se o pino 34 da Raspberry Pi está ligado ao pino GND da Ponte-H L298N e ao pino negativo do Case de Pilhas.
6. **Teste Inicial:** Ligue o Powerbank para validar os LEDs indicadores das placas antes de encaixar o Case de Pilhas.

## 4. Esquema Elétrico de ligações
![Esquema Elétrico do Robô Rover](rover_wiring_diagram.png)