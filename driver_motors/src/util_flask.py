from flask import Flask, render_template_string
from gpiozero import Robot

# Mesma definição de pinos do seu arquivo main.py
l1 = 11
l2 = 12
r1 = 15
r2 = 16
motor = Robot(left=(l1, l2), right=(r1, r2))
velocidade = 0.6

app = Flask(__name__)

# HTML para a página de controle
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Controle do Rover</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="text-align: center; font-family: sans-serif;">
    <h1>Controle do Rover</h1>
    <form action="/comando" method="post">
        <button name="direcao" value="frente" style="font-size: 24px; width: 100px; height: 100px;">&uarr;</button><br><br>
        <button name="direcao" value="esquerda" style="font-size: 24px; width: 100px; height: 100px;">&larr;</button>
        <button name="direcao" value="parar" style="font-size: 24px; width: 100px; height: 100px; background-color: red; color: white;">PARAR</button>
        <button name="direcao" value="direita" style="font-size: 24px; width: 100px; height: 100px;">&rarr;</button><br><br>
        <button name="direcao" value="re" style="font-size: 24px; width: 100px; height: 100px;">&darr;</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/comando', methods=['POST'])
def comando():
    direcao = request.form['direcao']
    if direcao == 'frente':
        motor.forward(velocidade)
    elif direcao == 're':
        motor.backward(velocidade)
    elif direcao == 'esquerda':
        motor.left(velocidade)
    elif direcao == 'direita':
        motor.right(velocidade)
    elif direcao == 'parar':
        motor.stop()
    return index()

if __name__ == '__main__':
    # Use o IP da sua Raspberry Pi para acessar de outros dispositivos
    app.run(host='0.0.0.0', port=5000)