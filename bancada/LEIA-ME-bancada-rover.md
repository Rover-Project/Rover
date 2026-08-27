# Bancada `raspberrypi-rover` — mapa da máquina

> Cópia canônica versionada. A mesma coisa está em `~/LEIA-ME.md` na placa;
> ao editar uma, atualize a outra.

Última organização: **2026-08-27**. Este arquivo é o ponto de entrada de quem
entra por SSH nesta placa. Se algo aqui divergir da realidade, corrija o arquivo
junto com a mudança.

Acesso: `ssh rover@100.93.21.122` (Tailscale, nó `raspberrypi-rover`).

---

## 1. O que é esta placa

Raspberry Pi 5 de **4 GB** (3 GB utilizáveis) montada no chassi do Brookstone
Rover 1.0. É a placa **do robô** — não confundir com a `raspberrypi-aihat`
(8 GB + Hailo-8L), que é a bancada de benchmark e **não** está no chassi.

| Item | Estado em 2026-08-27 |
|---|---|
| Python do sistema | 3.13.5 |
| Câmera | **imx519** (`dtoverlay=imx519,cam0`) — 4656×3496, modos 1280×720@80 e 1920×1080@60 |
| UART | habilitada (`dtparam=uart0=on`) → `/dev/serial0`, `/dev/ttyAMA0` — é por aqui que o TF-Luna fala |
| I²C | `/dev/i2c-1` livre — PCA9685 (pan/tilt) |
| Acelerador | **nenhum**. Sem Hailo no PCIe, sem `hailortcli` |
| Térmico | ocioso ~48 °C, `throttled=0x0` |

**Consequência prática:** modelos de aprendizado profundo não rodam em tempo real
aqui. Profundidade e detecção pesadas ou vão para o servidor pela rede, ou esperam
o AI HAT ser montado no chassi.

### Telemetria de energia sem hardware extra

O PMIC do Pi 5 expõe corrente e tensão por trilho — útil para medir custo
energético de computação:

```bash
vcgencmd pmic_read_adc      # corrente (A) e tensão (V) por trilho
vcgencmd measure_temp
vcgencmd get_throttled      # 0x0 = limpo; bit 0 = subtensão; bit 3 = throttling térmico
```

Ressalva: os trilhos do PMIC **não incluem os motores**, que vêm da bateria
separada pela ponte H. Isso mede o custo da computação, não o da locomoção.

---

## 2. Mapa das pastas

### Repositórios versionados

| Pasta | Repo | Branch | Papel |
|---|---|---|---|
| `~/Rover` | `Rover-Project/Rover` | **`testes`** | a `roverLib`. Branch de trabalho da equipe |
| `~/rover-benchmark` | `Rover-Project/rover-benchmark` | `main` | arnês de medição (está atrás do origin — `git pull` antes de usar) |

Ambientes virtuais: `~/Rover/.venv` e `~/rover-benchmark/.venv-edge`.

### Pastas de trabalho (sem git — vivem só nesta placa)

| Pasta | O que é | Cuidado |
|---|---|---|
| `~/coleta360/` | captura panorâmica com pan/tilt + manifesto de pose. Duas coletas em `saidas/` (06/08) | ver §3 |
| `~/pca9685/` | driver dos servos pan/tilt | **não mover** — `coleta360` importa daqui por caminho absoluto (`--pca-path`, padrão `~/pca9685`) |
| `~/demo-profundidade-api/` | demo de profundidade via API + `models/` (`efficientdet_lite0.tflite`, `gesture_recognizer.task`) | — |
| `~/vc-2026-1/` | material da disciplina de Visão Computacional (organizado em 06/08) | — |
| `~/Downloads/` | kit de instalação do libcamera para a imx519 (`install_pivariety_pkgs.sh` + `.deb`) | manter — é o que reinstala a câmera |
| `~/Imagens/`, `~/Vídeos/` | capturas de tela e vídeos de teste do usuário | — |

### Arquivo morto

`~/_arquivo/20260827/` — o que saiu do `$HOME` nesta organização. **Nada foi
apagado.** Ver `MANIFESTO.md` lá dentro para o que é cada coisa e por que saiu.

---

## 3. Ressalvas que já custaram tempo

**A mecânica de pan/tilt tem folga.** Medido em 06/08: o eixo de *tilt* só
percorre curso livre numa janela de ~10° de comando, e o mesmo comando não repete
a mesma posição. O ângulo gravado no manifesto é **o comando enviado**, não uma
leitura de posição. Trate como aproximado.

**O trilho V+ do PCA9685 precisa de alimentação própria.** A lógica do chip vive
dos 3,3 V do I²C, então ele responde no barramento e escreve os pulsos certos
*enquanto nenhum servo se mexe*. Se os servos estiverem parados, confira a
alimentação antes de suspeitar do código.

**A coleta `20260806_210415` não serve para reconstrução 3D.** É uma varredura de
pan com o corpo do robô parado — rotação pura não gera paralaxe. A coleta
`manual_20260806_221815` (38 frames) serve parcialmente: reconstruiu 21 das 38
câmeras, com geometria mal condicionada. Para reconstrução é preciso **deslocar o
robô**, não girar a câmera.

**Energia.** A linha lógica é alimentada por powerbank e a de potência por
suporte de pilhas. Sob carga já houve registro de `throttled=0xf0008` —
throttling térmico *e* subtensão ao mesmo tempo.

---

## 4. Antes de rodar qualquer coisa que mova o robô

1. O rover fica **na bancada** por padrão. Movimento só com autorização explícita
   de quem estiver conduzindo o experimento.
2. Toda rotina de movimento precisa de limite de tempo (`--seconds`) e de um
   caminho de parada dos motores no `finally`.
3. Sequência segura: motores desconectados (só log) → rodas no ar → chão.

---

## 5. Receitas rápidas

```bash
# câmera: confirmar que o sensor aparece
rpicam-hello --list-cameras

# LiDAR TF-Luna (UART)
ls -l /dev/serial0

# servos: diagnóstico sem mover o robô
python3 ~/coleta360/diagnostico_servos.py --help

# estado térmico e de energia durante um ensaio
watch -n1 'vcgencmd measure_temp; vcgencmd get_throttled'
```
