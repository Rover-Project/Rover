"""
Aula 6 - Projeto integrador: buscar e se aproximar de uma bola vermelha.

Esqueleto do projeto. O laço principal já funciona; complete as partes marcadas
com TODO. Por padrão roda no MUNDO SIMULADO (sem câmera nem robô):

    python aula6_projeto/main.py              # mundo simulado (PC)
    python aula6_projeto/main.py --real       # câmera e Lidar do Rover (ou webcam no PC)

Estados sugeridos:
    BUSCAR    -> gira devagar até ver a bola
    ALINHAR   -> gira com PID até a bola ficar no centro
    APROXIMAR -> avança corrigindo a direção, até o Lidar marcar DISTANCIA_ALVO
    CHEGOU    -> para
"""
import sys
import time
from pathlib import Path

import cv2

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "aula5_controle"))
from mundo import MundoSimulado  # noqa: E402
from controlador import PID  # noqa: E402
from roverlib import Rover, ProcessingImage  # noqa: E402

REAL = "--real" in sys.argv
# No mundo simulado a câmera não é usada (os frames vêm do mundo)
CONFIG = AQUI.parent / ("config_visao.yaml" if REAL else "config.yaml")

DISTANCIA_ALVO = 30        # cm: onde parar
PERIODO = 1 / 15           # s: período do laço (15 Hz)
DURACAO_MAXIMA = 40        # s
pid_giro = PID(kp=40, ki=10, limite=50)


# ---------------------------------------------------------------- percepção
def perceber(frame, distancia_cm):
    """
    Extrai do frame e do Lidar o que a decisão precisa.

    Returns:
        dict com: visto (bool), erro (-1 a 1, positivo = bola à direita),
        area (fração da imagem) e distancia (cm ou None).
    """
    mascara = ProcessingImage.color_segmentation(frame)
    m = cv2.moments(mascara, binaryImage=True)
    altura, largura = mascara.shape
    area = m["m00"] / (largura * altura)
    if area < 0.0005:
        return {"visto": False, "erro": 0.0, "area": 0.0, "distancia": distancia_cm}
    cx = m["m10"] / m["m00"]
    return {"visto": True, "erro": (cx - largura / 2) / (largura / 2), "area": area,
            "distancia": distancia_cm}


# ---------------------------------------------------------------- decisão
def decidir(estado, p):
    """Transições da máquina de estados. Retorna o próximo estado."""
    if estado == "BUSCAR" and p["visto"]:
        return "ALINHAR"
    if estado == "ALINHAR":
        if not p["visto"]:
            return "BUSCAR"
        if abs(p["erro"]) < 0.08:
            return "APROXIMAR"
    if estado == "APROXIMAR":
        # TODO 1: voltar a BUSCAR se perder a bola
        # TODO 2: ir para CHEGOU quando p["distancia"] <= DISTANCIA_ALVO
        #         (cuidado: a distância pode ser None)
        pass
    return estado


# ---------------------------------------------------------------- ação
def agir(estado, p, dt):
    """Velocidades (direita, esquerda) para o estado atual."""
    if estado == "BUSCAR":
        return -25, 25                         # gira devagar para a direita
    if estado == "ALINHAR":
        u = pid_giro(p["erro"], dt)
        return -u, u
    if estado == "APROXIMAR":
        # TODO 3: avançar com velocidade base (ex.: 35) e somar uma correção de giro
        #         proporcional ao erro, para não perder a bola enquanto anda
        return 0, 0
    return 0, 0                                # CHEGOU


# ---------------------------------------------------------------- laço principal
def main():
    mundo = None if REAL else MundoSimulado()
    with Rover.from_config(CONFIG) as rover:
        if not REAL:
            rover.lidar.verbose = False
        estado, inicio, anterior = "BUSCAR", time.monotonic(), time.monotonic()

        while time.monotonic() - inicio < DURACAO_MAXIMA and estado != "CHEGOU":
            agora = time.monotonic()
            dt, anterior = max(agora - anterior, 1e-3), agora

            if REAL:
                frame = rover.camera.get_frame()
                if frame is None:
                    continue
            else:
                mundo.atualizar(dt)
                frame = mundo.frame()
                rover.lidar.set_distance(mundo.distancia_lidar_cm())

            p = perceber(frame, rover.lidar.get_distance())
            novo = decidir(estado, p)
            if novo != estado:
                print(f"t={agora - inicio:5.1f} s  {estado} -> {novo}   {mundo or ''}")
                estado = novo
                pid_giro.reiniciar()

            vel_d, vel_e = agir(estado, p, dt)
            rover.move.move(speed_right=vel_d, speed_left=vel_e)
            if mundo:
                mundo.comandar(vel_d, vel_e)
            time.sleep(PERIODO)

        rover.move.stop()
        print(f"Fim: estado {estado}. {mundo or ''}")


if __name__ == "__main__":
    main()
