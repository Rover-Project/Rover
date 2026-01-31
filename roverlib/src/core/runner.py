from pathlib import Path
import subprocess

def run_project(path="."):
    path = Path(path)
    main_file = path / "main.py"

    if not main_file.exists():
        raise FileNotFoundError("Arquivo main.py não encontrado.")

    subprocess.run(["python", str(main_file)])
