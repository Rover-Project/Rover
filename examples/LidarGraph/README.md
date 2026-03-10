# MONITOR EM TEMPO REAL DAS INFORMAÇÕES ADQUIRIDAS PELO LIDAR

## FUNCIONAMENTO:

O script lidarGraph tem como objetivo a plotagem em tempo real das informações adquiridas pelo Lidar em um gráfico de linhas.

Logo após iniciar o Lidar com a função provida pelo plugin da roverLib, temos a definição da função **updateGraph**. Essa captura a ultima leitura do Lidar (também pela função provida pela biblioteca) e inicialmente armazena as informações adquiridas em três listas: distância, força do sinal e temperatura do chip. Com essas, atualizamos o x e y das linhas plotadas a partir da função **set_data()**, e a estrutura desse a partir da **set_xlim()**, retornando as linhas atualizadas para o renderizador da animação.

Posteriormente, são iniciados a fig (plano de fundo) e os dois eixos do gráfico (Para melhor visualização , a distância é plotada em um plano diferente da força e temperatura) e com os eixos configurados com títulos e legendas, chamamos a função **FuncAnimation()**, que até ser interrompida, utiliza a função **updateGraph()** para atualizar os elementos visuais previamente instanciados, gerenciando o intervalo de atualização.

## REQUISITOS DO SCRIPT:

REQUISITOS PARA RODAR O SCRIPT

Para garantir o funcionamento da plotagem em tempo real, o ambiente deve possuir:

- Python 3.x: Interpretador base.

- roverLib: Biblioteca core do projeto para interface com o hardware.

- Matplotlib: Responsável pela renderização gráfica e motor de animação.

- Numpy: (Geralmente necessário para manipulação eficiente dos arrays de dados das listas).

- Hardware: Sensor Lidar (conectado e configurado via serial/I2C conforme definido na roverLib) ou o simulador da biblioteca ativo.

## COMO RODAR:

**1. Conexão do Hardware**: Certifique-se de que o Lidar está alimentado e com os pinos de dados (RX/TX) conectados corretamente ao controlador.

2. Atualize o instalador de pacotes do sistema.

```bash
sudo apt update && sudo apt upgrade -y
```

3. Instale Python 3 e pip (caso não tenha):

```bash
sudo apt install python3 python3-pip -y
```

```bash
git clone "https://github.com/AbstractGleidson/Rover.git"
```

4. Realize a configuração da roverlib como especificado no README da biblioteca.

5. Execução: No terminal, dentro do diretório raiz do projeto, execute:

```bash
python -m examples.lidarTest.lidarGraph.main
```

6. Interação: Uma janela do Matplotlib será aberta. O gráfico será atualizado automaticamente até que a janela seja fechada ou o processo interrompido com Ctrl+C.

---