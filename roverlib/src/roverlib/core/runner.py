from pathlib import Path
import subprocess
import sys


def run_project(path=".") -> int:
    """
    Executa o main.py de um projeto Rover com o mesmo interpretador Python
    em que a RoverLib está instalada (respeitando o ambiente virtual).

    Retorna:
        O código de saída do programa.
    """
    path = Path(path).resolve()
    main_file = path / "main.py"

    if not main_file.exists():
        raise FileNotFoundError(f"Arquivo main.py não encontrado em '{path}'.")

    # cwd=path: o projeto encontra seu config.yaml e sua pasta src/
    result = subprocess.run([sys.executable, str(main_file)], cwd=path)
    return result.returncode
