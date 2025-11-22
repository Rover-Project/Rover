# Controle de Motores DC com Raspberry Pi e Ponte H L298N via interface gráfica(Tkinter)

Permite controlar dois motores DC conectados a uma **Raspberry Pi** através de uma **ponte H L298N** usando uma interface gráfica básica. 

---

## Funcionalidades

- **Seta ↑**: Motor para frente  
- **Seta ↓**: Motor para trás  
- **Seta ←**: Giro para a esquerda  
- **Seta →**: Giro para a direita  
- **+ Velocidade**: aumenta a velocidade dos motores no intervalo ``[0.1, 1]``  
- **- Velocidade**: diminui a velocidade dos motores  no intervalo ``[0.1, 1]``

---

## Requisitos
- Raspberry Pi (qualquer modelo com GPIO)
- Ponte H L298N
- Dois motores DC  
- Python 3  
- Bibliotecas listadas no arquivo `requirements.txt`  
---

## Conexão dos Motores Ponte H L298N
| Motor          | IN1/IN2 | GPIO Raspberry Pi |
| -------------- | ------- | ----------------- |
| Motor esquerdo | IN1/IN2 | x1 / x2           |
| Motor direito  | IN3/IN4 | y2 / y2           |

- **Enable** do L298N deve ser ligado ao VCC adequado (fonte >= 6V).

- **GND** da ponte H deve estar conectado ao GND da Raspberry Pi.

# Estrutura do código (Classes)
O código foi dividido em duas classes com responsabilidades bem definidas:

## 1- Motor
- **Responsabilidade**: Gerenciar a interação direta com os pinos GPIO e o controle dos motores **(Lógica de Baixo Nível)**.
- Utiliza a biblioteca **gpiozero.Robot** para abstrair o controle dos motores.
- Encapsula as funções básicas de movimento (``forward()``, ``backward()``, ``left()``, ``right()``, ``stop()``).
- Gerencia a **velocidade** atual dos motores.

## 2 - AppControllerMotor
- **Responsabilidade**: Gerenciar a Interface Gráfica (Tkinter) e a Lógica de eventos dos botões.

- Cria a janela, botões e labels de velocidade.

- Utiliza uma instância da classe Motor para realizar os comandos de movimento.

- Gerencia o estado dos botões (forward_pressed, etc.) e usa o método ``root.after()`` do Tkinter para criar um loop de movimento contínuo enquanto o botão é pressionado (detecção de longa pressão).

## Uso

1. Atualize o sistema:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Instale Python 3 e pip (caso não tenha):
```bash
sudo apt install python3 python3-pip -y
```

3. Clone o repositório com os drivers:
````bash
git clone "https://github.com/AbstractGleidson/Rover.git"
````

4. Instale todas as dependências usando o **requirements.txt**:
```bash
pip install -r requirements.txt
```

5. Navegue para a pasta dos driver de motor:
````bash
cd Rover/driver_motors
````


6. Execute o programa com privilégios de root:

````bash
sudo python main.py
````
---