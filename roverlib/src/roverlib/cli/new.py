import click # type: ignore
from pathlib import Path
import importlib.resources as resources

# Arquivos/pastas do template que não devem ser copiados para o projeto do usuário
_IGNORE = {"__pycache__", ".pytest_cache"}


def _copy_template(source, target: Path):
    """Copia recursivamente o template (funciona mesmo se o pacote estiver compactado)."""
    target.mkdir(parents=True)
    for item in source.iterdir():
        if item.name in _IGNORE or item.name.endswith(".pyc"):
            continue
        if item.is_dir():
            _copy_template(item, target / item.name)
        else:
            (target / item.name).write_bytes(item.read_bytes())


@click.command()
@click.argument("name")
def new(name: str):
    """Cria um projeto Rover."""
    target = Path.cwd() / name

    if target.exists():
        raise click.ClickException(
            f"Diretório '{name}' já existe."
        )

    template = resources.files("roverlib.cli").joinpath("templates", "project")
    if not template.is_dir():
        raise click.ClickException(
            "Template de projeto não encontrado na instalação da RoverLib. "
            "Reinstale com: pip install --force-reinstall roverlib[cli]"
        )

    _copy_template(template, target)

    click.echo(f"Projeto '{name}' criado com sucesso!")
    click.echo(f"Para executar: rover run {name}")
