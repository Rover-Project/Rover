# Tutoriais da RoverLib

Código das aulas da trilha **Aprender** da documentação (`docs/aprender/`), voltada a disciplinas de visão computacional, robótica e inteligência artificial.

| Pasta | Aula |
|---|---|
| `aula1_locomocao/` | Locomoção diferencial e malha aberta |
| `aula2_sensores/` | Sensores de distância, ruído e máquinas de estados |
| `aula3_imagem/` | Imagem digital e espaços de cor |
| `aula4_deteccao/` | Detecção de objetos por cor e forma |
| `aula5_controle/` | Controle realimentado por visão |
| `aula6_projeto/` | Projeto integrador |

Execute os scripts **a partir desta pasta** (`tutoriais/`), por exemplo:

```bash
python aula1_locomocao/primeiros_comandos.py
```

As aulas 1 e 2 usam o `config.yaml` (motores e Lidar); as aulas 3 a 6 usam o `config_visao.yaml`, que acrescenta a câmera.

Todos rodam no PC: motores e Lidar são simulados, e as figuras são salvas na pasta `saida/` de cada aula. Os scripts que usam a câmera ao vivo precisam de uma webcam no PC ou da câmera do Rover. No Rover, o mesmo código move o robô de verdade; para testar sem mover as rodas, use `ROVER_SIMULATE=1`.
