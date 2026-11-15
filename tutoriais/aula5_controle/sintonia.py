"""
Aula 5 - Sintonia de controladores em uma planta simulada.

Simula o Rover girando para centralizar um alvo na imagem:

- o alvo está fixo, 30° à direita da direção inicial do robô;
- a câmera tem campo de visão de 62° e 640 px de largura (modelo pinhole);
- o erro é a posição horizontal do alvo na imagem, normalizada em [-1, 1];
- o motor tem zona morta (comandos pequenos não giram o robô) e resposta lenta
  (atraso de primeira ordem), e a visão chega com um quadro de atraso.

Compara P, P com ganho alto, PI e PID e salva o gráfico do erro no tempo.

Executar (na pasta tutoriais/):  python aula5_controle/sintonia.py
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlador import PID  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "saida"

# ---------------- modelo da câmera e do robô ----------------
LARGURA = 640
FOV = math.radians(62)
FOCAL = (LARGURA / 2) / math.tan(FOV / 2)     # distância focal em pixels
ALVO = math.radians(30)                         # direção do alvo
DT = 1 / 30                                     # 30 quadros por segundo
DURACAO = 4.0
GANHO_MOTOR = math.radians(2.0)                 # rad/s por unidade de velocidade (100 -> ~200°/s)
ZONA_MORTA = 12                                 # comandos menores que isso não giram o robô
TAU = 0.15                                      # constante de tempo do motor (s)


def erro_na_imagem(theta):
    """Erro normalizado [-1, 1] do alvo na imagem, ou None se ele estiver fora do campo de visão."""
    angulo = ALVO - theta
    if abs(angulo) > FOV / 2:
        return None
    x = LARGURA / 2 + FOCAL * math.tan(angulo)
    return (x - LARGURA / 2) / (LARGURA / 2)


def simular(controlador):
    theta, omega = 0.0, 0.0
    erro_visto = erro_na_imagem(theta)           # a visão chega com um quadro de atraso
    tempos, erros = [], []
    for k in range(int(DURACAO / DT)):
        u = controlador(erro_visto, DT) if erro_visto is not None else 0.0
        u_efetivo = 0.0 if abs(u) < ZONA_MORTA else u
        omega += (GANHO_MOTOR * u_efetivo - omega) * DT / TAU     # motor de primeira ordem
        theta += omega * DT
        erro_visto = erro_na_imagem(theta)
        tempos.append(k * DT)
        erros.append(math.degrees(ALVO - theta))
    return tempos, erros


def metricas(tempos, erros, faixa=1.0):
    """Sobressinal (°), tempo de acomodação (s, dentro de ±faixa graus) e erro final (°)."""
    sobressinal = max(0.0, -min(erros))
    fora = [t for t, e in zip(tempos, erros) if abs(e) > faixa]
    if fora and fora[-1] >= tempos[-1]:
        acomodacao = None                     # não entrou na faixa até o fim da simulação
    else:
        acomodacao = fora[-1] + DT if fora else 0.0
    return sobressinal, acomodacao, erros[-1]


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    casos = {
        "P (kp=40)": PID(kp=40),
        "P (kp=250)": PID(kp=250),
        "PI (kp=40, ki=20)": PID(kp=40, ki=20),
        "PI (kp=40, ki=60)": PID(kp=40, ki=60),
        "PID (kp=80, ki=30, kd=6)": PID(kp=80, ki=30, kd=6),
    }

    print(f"{'controlador':26s} {'sobressinal':>12s} {'acomodação':>11s} {'erro final':>11s}")
    plt.figure(figsize=(9, 5))
    for nome, controlador in casos.items():
        tempos, erros = simular(controlador)
        s, ta, ef = metricas(tempos, erros)
        texto_ta = f"{ta:8.2f} s" if ta is not None else "não acomoda"
        print(f"{nome:26s} {s:10.1f} °  {texto_ta:>11s}  {ef:9.2f} °")
        plt.plot(tempos, erros, label=nome)

    plt.axhline(0, color="k", linewidth=0.8)
    plt.xlabel("tempo (s)")
    plt.ylabel("erro de direção (°)")
    plt.title("Centralizando um alvo 30° à direita")
    plt.legend()
    plt.grid(True)
    arquivo = SAIDA / "sintonia.png"
    plt.savefig(arquivo, dpi=120)
    print(f"\nGráfico salvo em {arquivo}")
