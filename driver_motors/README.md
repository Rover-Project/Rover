# Controle de Motores DC com Raspberry Pi e Ponte H L298N via Teclado

Permite controlar dois motores DC conectados a uma **Raspberry Pi** através de uma **ponte H L298N** usando o teclado. As setas direcionais controlam a direção dos motores, e a barra de espaço os para.

---

## Funcionalidades

- **Seta ↑**: Motor para frente  
- **Seta ↓**: Motor para trás  
- **Seta ←**: Giro para a esquerda  
- **Seta →**: Giro para a direita  
- **Espaço**: Para os motores  
- **Q**: Encerra o programa  

---

## Requisitos

- Raspberry Pi (qualquer modelo com GPIO)  
- Python 3  
- Bibliotecas listadas no arquivo `requirements.txt`  
---
## Conexão dos Motores Ponte H L298N
| Motor          | IN1/IN2 | GPIO Raspberry Pi |
| -------------- | ------- | ----------------- |
| Motor esquerdo | IN1/IN2 | x / x            |
| Motor direito  | IN3/IN4 | y / y           |

- **Enable** do L298N deve ser ligado ao VCC adequado (fonte >= 6V).

- **GND** da ponte H deve estar conectado ao GND da Raspberry Pi.

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

4. Navegue para a pasta dos driver de motor:
````bash
cd Rover/driver_motors
````

6. Instale todas as dependências usando o **requirements.txt**:
```bash
pip install -r requirements.txt
```

5. Execute o programa com privilégios de root:

````bash
sudo python3 src/main.py
````
---
