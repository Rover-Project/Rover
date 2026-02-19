import click # type: ignore
from pathlib import Path
import shutil
import importlib.resources as resources

@click.command()
@click.argument("name")
def new(name: str):
    """Cria um projeto Rover."""
    base_dir = Path.cwd()
    target = base_dir / name

    if target.exists():
        raise click.ClickException(
            f"Diretório '{name}' já existe."
        )

    template = resources.files("roverlib.templates").joinpath("project")
    shutil.copytree(template, target) # type: ignore

    click.echo(f"Projeto '{name}' criado com sucesso!")
