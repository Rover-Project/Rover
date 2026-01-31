import click
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

    template = resources.files("rover.templates").joinpath("basic")
    shutil.copytree(template, target)

    click.echo(f"✅ Projeto '{name}' criado com sucesso!")
