import shutil
from pathlib import Path
import importlib.resources as resources

def create_project(name: str):
    target = Path(name)

    if target.exists():
        raise FileExistsError(f"Diretório '{name}' já existe.")

    template = resources.files("src.templates").joinpath("basic")
    shutil.copytree(template, target) # type: ignore
